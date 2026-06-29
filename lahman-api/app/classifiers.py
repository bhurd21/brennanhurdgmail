"""Turn one condition string into a SQL fragment + params, or None.

Team and award name → ID mapping is done by the DB (v_team_lookup,
v_award_lookup views). Classifiers only detect the category and pass the raw
display name as a query parameter; SQL does the lookup at query time.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import lookups


@dataclass
class Condition:
    category: str               # team | stat | position | award | player
    fragment: str               # name of the .sql file under sql/conditions/
    fields: dict = field(default_factory=dict)   # identifiers formatted into SQL template
    params: dict = field(default_factory=dict)   # values bound as query params


_COMPOUND_RE = re.compile(
    r"(\d+)\+\s+([A-Za-z0-9]+)\s+/\s+(\d+)\+\s+([A-Za-z0-9]+)\s+(Season|Career)", re.I
)
_STAT_RE = re.compile(r"(\.?\d+(?:\.\d+)?)\+?\s+([A-Za-z0-9]+)\s+(Season|Career)", re.I)
_PLAYED_RE = re.compile(r"^Played\s+(.+?)\s+min\.\s+1\s+game$", re.I)


def _parse_value(tok: str) -> float:
    """Parse a threshold token like '300', '.300', or '3.00' into a float."""
    return float("0" + tok) if tok.startswith(".") else float(tok)


def _group(timeframe: str) -> str:
    """Return the SQL GROUP BY columns for season (per player-year) or career (per player)."""
    return '"playerID", "yearID"' if timeframe.lower() == "season" else '"playerID"'


def classify_team(text: str) -> Condition | None:
    if text not in lookups.KNOWN_TEAM_NAMES:
        return None
    # Pass the raw display name; team.sql joins v_team_lookup to resolve franchID.
    return Condition("team", "team", params={"team_name": text})


def classify_award(text: str) -> Condition | None:
    if text not in lookups.KNOWN_AWARD_NAMES:
        return None
    if text == "All Star":
        return Condition("award", "allstar")
    # Pass the raw display name; award.sql joins v_award_lookup to resolve awardID.
    return Condition("award", "award", params={"award_name": text})


def classify_player(text: str) -> Condition | None:
    entry = lookups.PLAYER_LOOKUP.get(text)
    if not entry:
        return None
    fragment, params = entry
    return Condition("player", fragment, params=dict(params))


def classify_position(text: str) -> Condition | None:
    t = text.strip()
    if re.fullmatch(r"Pitched\s+min\.\s+1\s+game", t, re.I):
        name = "Pitcher"
    elif re.fullmatch(r"Caught\s+min\.\s+1\s+game", t, re.I):
        name = "Catcher"
    elif re.fullmatch(r"Designated\s+Hitter\s+min\.\s+1\s+game", t, re.I):
        name = "Designated Hitter"
    else:
        m = _PLAYED_RE.match(t)
        if not m:
            return None
        name = m.group(1).strip()
    col = lookups.POSITION_LOOKUP.get(name)
    if not col:
        return None
    return Condition("position", "position", fields={"col": col})


def classify_stat(text: str) -> Condition | None:
    # Compound stat first ("30+ HR / 30+ SB Season Batting").
    compound_match = _COMPOUND_RE.search(text)
    if compound_match:
        threshold1, stat_tok1, threshold2, stat_tok2, timeframe = compound_match.groups()
        stat1 = lookups.STAT_LOOKUP.get(stat_tok1.upper())
        stat2 = lookups.STAT_LOOKUP.get(stat_tok2.upper())
        if not (stat1 and stat2 and stat1["kind"] == "count" and stat2["kind"] == "count"):
            return None
        return Condition(
            "stat", "stat_compound",
            fields={"table": stat1["table"], "group": _group(timeframe),
                    "col1": stat1["col"], "col2": stat2["col"]},
            params={"v1": _parse_value(threshold1), "v2": _parse_value(threshold2)},
        )

    if not re.search(r"\b(Season|Career)\b", text, re.I):
        return None
    stat_match = _STAT_RE.search(text)
    if not stat_match:
        return None
    threshold_tok, stat_tok, timeframe = stat_match.groups()
    stat = lookups.STAT_LOOKUP.get(stat_tok.upper())
    if not stat:
        return None
    value = _parse_value(threshold_tok)
    group = _group(timeframe)

    if stat["kind"] == "count":
        return Condition(
            "stat", "stat_count",
            fields={"table": stat["table"], "group": group,
                    "col": stat["col"], "op": stat["op"]},
            params={"value": value},
        )
    return Condition(
        "stat", "stat_rate",
        fields={"table": stat["table"], "group": group, "rate": stat["rate"],
                "op": stat["op"]},
        params={"value": value},
    )


_CLASSIFIERS = (
    classify_team,
    classify_award,
    classify_player,
    classify_position,
    classify_stat,
)


def classify(text: str) -> Condition | None:
    text = text.strip()
    for fn in _CLASSIFIERS:
        cond = fn(text)
        if cond is not None:
            return cond
    return None
