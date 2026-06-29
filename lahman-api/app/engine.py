"""The whole engine: split -> classify each half -> compose envelope -> run.

All SQL lives in app/sql/; this module only loads the right fragments,
namespaces their params, and slots them into the envelope.
"""
import logging
import re
from functools import lru_cache
from pathlib import Path

from . import classifiers, db

log = logging.getLogger("lahman.engine")

_SQL_DIR = Path(__file__).parent / "sql"
_SPLIT_RE = re.compile(r"\s\+\s")


@lru_cache(maxsize=None)
def _envelope() -> str:
    return (_SQL_DIR / "envelope.sql").read_text()


@lru_cache(maxsize=None)
def _fragment(name: str) -> str:
    return (_SQL_DIR / "conditions" / f"{name}.sql").read_text()


# obscure=False → prominent players first; obscure=True → most obscure first.
# These are safe SQL literals (not user input) slotted into the ORDER BY.
_ORDER = {
    False: "career_games DESC, last_season DESC NULLS LAST, player_id",
    True:  "career_games ASC,  last_season ASC  NULLS LAST, player_id",
}

# Plain season-stat fragment -> its team-tied combined counterpart.
_TEAM_STAT = {
    "stat_count":    "team_stat_count",
    "stat_rate":     "team_stat_rate",
    "stat_compound": "team_stat_compound",
}


def _is_season_stat(cond: classifiers.Condition) -> bool:
    return cond.category == "stat" and '"yearID"' in cond.fields.get("group", "")


def _build_side(cond: classifiers.Condition, prefix: str) -> tuple[str, dict]:
    """Render one condition's SQL with its params namespaced (a_/b_)."""
    sql = _fragment(cond.fragment).format(p=prefix, **cond.fields)
    params = {f"{prefix}{k}": v for k, v in cond.params.items()}
    return sql, params


def _normal_ctes(cond_a, cond_b, obscure: bool) -> tuple[str, dict]:
    """Two independent condition fragments, INTERSECTed on playerID."""
    frag_a, pa = _build_side(cond_a, "a_")
    frag_b, pb = _build_side(cond_b, "b_")
    ctes = (
        f"cond_a AS (\n{frag_a}\n),\n"
        f"cond_b AS (\n{frag_b}\n),\n"
        'matched_ids AS (\n'
        '    SELECT "playerID" FROM cond_a\n'
        '    INTERSECT\n'
        '    SELECT "playerID" FROM cond_b\n'
        '),\n'
    )
    return ctes, {**pa, **pb}


def _combined_ctes(team_cond, stat_cond, obscure: bool) -> tuple[str, dict]:
    """Team + single-season stat tied into one query (the season stat must be
    achieved WITH that team). Params use a fixed `c_` prefix."""
    body = _fragment(_TEAM_STAT[stat_cond.fragment]).format(**stat_cond.fields)
    params = {"c_team_name": team_cond.params["team_name"]}
    params.update({f"c_{k}": v for k, v in stat_cond.params.items()})
    # The combined query yields one row per qualifying season; dedup to one row
    # per player (INTERSECT in the normal path dedups for free).
    ctes = (
        f"qualifying AS (\n{body}\n),\n"
        'matched_ids AS (\n    SELECT DISTINCT "playerID" FROM qualifying\n),\n'
    )
    return ctes, params


def _team_position_ctes(team_cond, pos_cond) -> tuple[str, dict]:
    """Position played in a game for this specific team (grid rule)."""
    body = _fragment("team_position").format(col=pos_cond.fields["col"])
    params = {"c_team_name": team_cond.params["team_name"]}
    ctes = (
        f"qualifying AS (\n{body}\n),\n"
        'matched_ids AS (\n    SELECT DISTINCT "playerID" FROM qualifying\n),\n'
    )
    return ctes, params


def _team_ws_champ_ctes(team_cond) -> tuple[str, dict]:
    """WS Champ tied to team: player appeared for that team in its WS-winning season."""
    body = _fragment("team_ws_champ")
    params = {"c_team_name": team_cond.params["team_name"]}
    ctes = (
        f"qualifying AS (\n{body}\n),\n"
        'matched_ids AS (\n    SELECT DISTINCT "playerID" FROM qualifying\n),\n'
    )
    return ctes, params


def _team_award_ctes(team_cond, award_cond) -> tuple[str, dict]:
    """Award won in a season the player appeared for this team (grid rule)."""
    if award_cond.fragment == "allstar":
        body = _fragment("team_allstar")
        params = {"c_team_name": team_cond.params["team_name"]}
    else:
        body = _fragment("team_award")
        params = {
            "c_team_name":  team_cond.params["team_name"],
            "c_award_name": award_cond.params["award_name"],
        }
    ctes = (
        f"qualifying AS (\n{body}\n),\n"
        'matched_ids AS (\n    SELECT DISTINCT "playerID" FROM qualifying\n),\n'
    )
    return ctes, params


def _empty(question: str, category: str) -> dict:
    return {"question": question, "category": category, "count": 0, "players": [], "sql": None}


def _render_sql_display(sql: str, params: dict) -> str:
    """Interpolate psycopg params into SQL for human-readable display only."""
    result = sql
    for key, value in params.items():
        placeholder = f"%({key})s"
        replacement = f"'{value}'" if isinstance(value, str) else str(value)
        result = result.replace(placeholder, replacement)
    return result


def build(question: str, limit: int = 100, obscure: bool = False):
    """Compose the SQL for a question without executing it.

    Returns (sql, params, category). When the question can't be classified,
    sql/params are None and category is "unmatched". Pure and side-effect free;
    the natural seam for tests.
    """
    parts = [p.strip() for p in _SPLIT_RE.split(question.strip()) if p.strip()]
    if len(parts) != 2:
        return None, None, "unmatched"

    cond_a = classifiers.classify(parts[0])
    cond_b = classifiers.classify(parts[1])
    if cond_a is None or cond_b is None:
        return None, None, "unmatched"

    # Canonicalize: if either condition is a team, make it cond_a so every
    # team-pairing rule only needs to be written once.
    if cond_b.category == "team":
        cond_a, cond_b = cond_b, cond_a

    if cond_a.category != "team":
        ctes, params = _normal_ctes(cond_a, cond_b, obscure)
    elif _is_season_stat(cond_b):
        ctes, params = _combined_ctes(cond_a, cond_b, obscure)
    elif cond_b.category == "award":
        ctes, params = _team_award_ctes(cond_a, cond_b)
    elif cond_b.category == "position":
        ctes, params = _team_position_ctes(cond_a, cond_b)
    elif cond_b.fragment == "ws_champ":
        ctes, params = _team_ws_champ_ctes(cond_a)
    else:
        ctes, params = _normal_ctes(cond_a, cond_b, obscure)

    sql = _envelope().format(ctes=ctes, order=_ORDER[obscure])
    params["limit"] = limit
    category = "_".join(sorted([cond_a.category, cond_b.category]))
    return sql, params, category


async def answer(question: str, limit: int = 100, obscure: bool = False) -> dict:
    sql, params, category = build(question, limit, obscure)
    if sql is None:
        return _empty(question, category)

    try:
        rows = await db.fetch(sql, params)
    except Exception:
        log.exception("query failed for %r", question)
        return _empty(question, "error")

    return {
        "question": question,
        "category": category,
        "count": len(rows),
        "players": rows,
        "sql": _render_sql_display(sql, params),
    }
