"""Detection vocabulary for classifiers.

Team and award name → ID mappings now live in SQL (v_team_lookup,
v_award_lookup views). This module keeps only the sets needed to detect which
category a condition belongs to, plus the stat/position/player lookups that
still drive SQL generation.
"""

# Names that classify_team() recognises. The actual franchID mapping lives in
# the v_team_lookup DB view; Python only needs the keys for detection.
KNOWN_TEAM_NAMES: frozenset[str] = frozenset({
    "Arizona Diamondbacks",
    "Athletics",
    "Oakland Athletics",
    "Atlanta Braves",
    "Baltimore Orioles",
    "Boston Red Sox",
    "Chicago Cubs",
    "Chicago White Sox",
    "Cincinnati Reds",
    "Cleveland Guardians",
    "Colorado Rockies",
    "Detroit Tigers",
    "Houston Astros",
    "Kansas City Royals",
    "Los Angeles Angels",
    "Los Angeles Angels of Anaheim",
    "Los Angeles Dodgers",
    "Miami Marlins",
    "Milwaukee Brewers",
    "Minnesota Twins",
    "New York Mets",
    "New York Yankees",
    "Philadelphia Phillies",
    "Pittsburgh Pirates",
    "San Diego Padres",
    "San Francisco Giants",
    "Seattle Mariners",
    "St. Louis Cardinals",
    "Tampa Bay Rays",
    "Texas Rangers",
    "Toronto Blue Jays",
    "Washington Nationals",
})

# Award names that classify_award() recognises.
# "All Star" is special — it routes to allstar.sql (not award.sql).
# All others route to award.sql, which joins v_award_lookup for the awardID.
KNOWN_AWARD_NAMES: frozenset[str] = frozenset({
    "All Star",
    "Gold Glove",
    "Silver Slugger",
    "MVP",
    "Cy Young",
    "Rookie of the Year",
})

# Stat token (uppercased) → how to evaluate it.
#   kind="count": HAVING SUM("col") op value
#   kind="rate" : a computed expression (AVG, ERA)
STAT_LOOKUP = {
    "H":     {"kind": "count", "table": "Batting",  "col": "H",   "op": ">="},
    "HITS":  {"kind": "count", "table": "Batting",  "col": "H",   "op": ">="},
    "HR":    {"kind": "count", "table": "Batting",  "col": "HR",  "op": ">="},
    "RBI":   {"kind": "count", "table": "Batting",  "col": "RBI", "op": ">="},
    "RUN":   {"kind": "count", "table": "Batting",  "col": "R",   "op": ">="},
    "RUNS":  {"kind": "count", "table": "Batting",  "col": "R",   "op": ">="},
    "SB":    {"kind": "count", "table": "Batting",  "col": "SB",  "op": ">="},
    "2B":    {"kind": "count", "table": "Batting",  "col": "2B",  "op": ">="},
    "WIN":   {"kind": "count", "table": "Pitching", "col": "W",   "op": ">="},
    "WINS":  {"kind": "count", "table": "Pitching", "col": "W",   "op": ">="},
    "K":     {"kind": "count", "table": "Pitching", "col": "SO",  "op": ">="},
    "SAVE":  {"kind": "count", "table": "Pitching", "col": "SV",  "op": ">="},
    "SAVES": {"kind": "count", "table": "Pitching", "col": "SV",  "op": ">="},
    "AVG": {
        "kind": "rate", "table": "Batting", "op": ">=",
        "rate": 'SUM("H")::numeric / NULLIF(SUM("AB"), 0)',
    },
    "ERA": {
        "kind": "rate", "table": "Pitching", "op": "<=",
        "rate": 'SUM("ER")::numeric * 27 / NULLIF(SUM("IPouts"), 0)',
    },
}

# Position phrase target → Appearances game-count column.
# Supports both full names and common abbreviations used by Immaculate Grid.
POSITION_LOOKUP = {
    # Full names
    "Pitcher":           "G_p",
    "Catcher":           "G_c",
    "First Base":        "G_1b",
    "Second Base":       "G_2b",
    "Third Base":        "G_3b",
    "Shortstop":         "G_ss",
    "Left Field":        "G_lf",
    "Center Field":      "G_cf",
    "Right Field":       "G_rf",
    "Outfield":          "G_of",
    "Designated Hitter": "G_dh",
    # Abbreviations
    "P":   "G_p",
    "C":   "G_c",
    "1B":  "G_1b",
    "2B":  "G_2b",
    "3B":  "G_3b",
    "SS":  "G_ss",
    "LF":  "G_lf",
    "CF":  "G_cf",
    "RF":  "G_rf",
    "OF":  "G_of",
    "DH":  "G_dh",
}

# "Player"-style condition text → (fragment, params). All derived from Lahman.
# WAR / no-hitter / draft / Negro-League conditions are intentionally absent
# (no source data in lahman-db) and fall through to "unmatched".
PLAYER_LOOKUP = {
    "Hall of Fame":                        ("hall_of_fame",   {}),
    "Only One Team":                       ("one_team",       {}),
    "World Series Champ WS Roster":        ("ws_champ",       {}),
    "Played Major Leagues":                ("played_mlb",     {}),
    "Born Outside US 50 States and DC":    ("born_outside_us", {}),
    "United States":                       ("born_country",   {"country": "USA"}),
    "Canada":                              ("born_country",   {"country": "CAN"}),
    "Dominican Republic":                  ("born_country",   {"country": "D.R."}),
    "Puerto Rico":                         ("born_country",   {"country": "P.R."}),
    "Played In Major Negro Lgs":           ("negro_leagues",  {}),
    "Threw a No-Hitter":                   ("no_hitter",      {}),
}
