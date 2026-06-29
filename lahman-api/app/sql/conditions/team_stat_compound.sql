-- Team + single-season compound stat (e.g. 30 HR / 30 SB), tied together: both
-- thresholds must be met WITH this team in the same season.
-- v_team_lookup resolves the display name to franchID.
SELECT b."playerID"
FROM {table} b
JOIN (
    SELECT t."yearID", t."teamID"
    FROM Teams t
    JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
    WHERE vl.name = %(c_team_name)s
) ft ON ft."yearID" = b."yearID" AND ft."teamID" = b."teamID"
GROUP BY b."playerID", b."yearID"
HAVING SUM(b."{col1}") >= %(c_v1)s
   AND SUM(b."{col2}") >= %(c_v2)s
