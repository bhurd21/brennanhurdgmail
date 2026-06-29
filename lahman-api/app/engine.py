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


def _drop_floor(fields: dict, obscure: bool) -> dict:
    """In obscure mode, blank the rate-stat playing-time floor so marginal
    players that would normally be filtered out are surfaced."""
    fields = dict(fields)
    if obscure and "floor_clause" in fields:
        fields["floor_clause"] = ""
    return fields


def _is_season_stat(cond: classifiers.Condition) -> bool:
    return cond.category == "stat" and '"yearID"' in cond.fields.get("group", "")


def _build_side(cond: classifiers.Condition, prefix: str, obscure: bool) -> tuple[str, dict]:
    """Render one condition's SQL with its params namespaced (a_/b_)."""
    fields = _drop_floor(cond.fields, obscure)
    sql = _fragment(cond.fragment).format(p=prefix, **fields)
    params = {f"{prefix}{k}": v for k, v in cond.params.items()}
    return sql, params


def _normal_ctes(cond_a, cond_b, obscure: bool) -> tuple[str, dict]:
    """Two independent condition fragments, INTERSECTed on playerID."""
    frag_a, pa = _build_side(cond_a, "a_", obscure)
    frag_b, pb = _build_side(cond_b, "b_", obscure)
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
    fields = _drop_floor(stat_cond.fields, obscure)
    body = _fragment(_TEAM_STAT[stat_cond.fragment]).format(**fields)
    params = {"c_team_name": team_cond.params["team_name"]}
    params.update({f"c_{k}": v for k, v in stat_cond.params.items()})
    # The combined query yields one row per qualifying season; dedup to one row
    # per player (INTERSECT in the normal path dedups for free).
    ctes = (
        f"qualifying AS (\n{body}\n),\n"
        'matched_ids AS (\n    SELECT DISTINCT "playerID" FROM qualifying\n),\n'
    )
    return ctes, params


def _empty(question: str, category: str) -> dict:
    return {"question": question, "category": category, "count": 0, "players": []}


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

    # Team + single-season stat: tie the stat to the team (grid rule). Career
    # stats stay career-wide, so they keep the plain INTERSECT.
    if cond_a.category == "team" and _is_season_stat(cond_b):
        ctes, params = _combined_ctes(cond_a, cond_b, obscure)
    elif cond_b.category == "team" and _is_season_stat(cond_a):
        ctes, params = _combined_ctes(cond_b, cond_a, obscure)
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
    }
