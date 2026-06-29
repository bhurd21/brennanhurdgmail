# Implementation Notes

Context for how the API maps official Immaculate Grid rules to SQL.

## Rule → SQL Routing

The engine classifies each half of a question into a category, then picks the right SQL path:

| Condition pair | Routing | Why |
|---|---|---|
| Team + Season stat | `team_stat_count/rate/compound.sql` | Stat must be achieved WITH that team in one season |
| Team + Award (MVP, CY, GG, SS, ROY) | `team_award.sql` | Award must be won in a season player appeared for that team |
| Team + All-Star | `team_allstar.sql` | Same year-coupling as awards |
| Team + Position | `team_position.sql` | Position must be played in a game FOR that team |
| Team + World Series Champ | `team_ws_champ.sql` | Player must have been on that specific team when it won the WS |
| Team + Career stat | INTERSECT | Career stats only require the player to have played for the team "at any point" |
| Team + HOF / Born / One Team | INTERSECT | No year coupling required by the rules |
| Stat + Stat / Award + Award / etc. | INTERSECT | "Does not necessarily need to be in the same season" |

## Year-Coupling Principle

A key pattern: any rule that says "when paired with a team, must have [done X] in a season he appeared for that team" requires a JOIN between the qualifying event and the Appearances table on `yearID`. Simple INTERSECT is wrong for these because a player who won the award with Team A and played for Team B (but never won with Team B) would incorrectly qualify for "Team B + Award."

Rules that do NOT require year coupling (INTERSECT is correct):
- Career stats: "simply had to play for the team at any point"
- Hall of Fame: "must have played a major league game for the team in question"
- Born conditions: purely biographical
- "Only One Team": standalone check

## Known Unsupported Conditions

These conditions appear on real Immaculate Grids but are not implemented because the Lahman database does not contain the required source data:

- **6+ WAR Season / 40+ WAR Career** — no WAR data in Lahman (Baseball Reference proprietary)
- **First Round Draft Pick** — no draft data in Lahman

Questions containing these conditions return `"category": "unmatched"` with an empty player list.

## AVG / ERA: No Minimum Requirement

The official rules explicitly state no minimum plate appearance or innings requirement for AVG and ERA in both season and career contexts. There are no floors applied; a player with 1 AB and 1 hit qualifies for .300+ AVG Career.

## "Only One Team" and Historical Leagues

The rule qualifies players who played for "only one major league franchise, OR only one AL/NL team." The Lahman database includes players from historical leagues (AA 1882-1891, PL 1890, UA 1884, FL 1914-1915, NA 1871-1875). A player who had multiple franchises across those old leagues but only one AL/NL franchise still qualifies via the second arm of the HAVING clause.

## Split-Season Stats

For team + season stat, each row in the Batting/Pitching table represents one player-team-season stint. The query joins to only the target team's rows, so a mid-season trade correctly isolates stats to each team. Example: J.D. Martinez 2017 (16 HR Detroit + 29 HR Arizona) matches neither "Detroit Tigers + 40+ HR Season" nor "Arizona Diamondbacks + 40+ HR Season."

## Team Name Resolution

All 30 current franchises are supported by display name. Relocations and aliases are handled in the `v_team_lookup` database view (e.g., "Miami Marlins" → `FLA` franchID, covering both Florida Marlins and Miami Marlins eras; "Washington Nationals" → `WSN`, covering both the Expos' Washington era and the Nationals).
