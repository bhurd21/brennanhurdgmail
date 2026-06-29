-- Team + single-season counting stat, tied together: the threshold must be met
-- WITH this team in one season. v_team_lookup resolves the display name to
-- franchID; `ft` keeps only this franchise's (year, team) rows, so a split
-- season contributes only its per-team portion
-- (e.g. J.D. Martinez 2017: 16 HR Detroit, 29 Arizona -> neither meets 40).
SELECT b."playerID"
FROM {table} b
JOIN (
    SELECT t."yearID", t."teamID"
    FROM Teams t
    JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
    WHERE vl.name = %(c_team_name)s
) ft ON ft."yearID" = b."yearID" AND ft."teamID" = b."teamID"
GROUP BY b."playerID", b."yearID"
HAVING SUM(b."{col}") {op} %(c_value)s
