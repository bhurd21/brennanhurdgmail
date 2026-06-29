-- Team + single-season rate stat (AVG/ERA), tied together: the rate must be met
-- using only this team's portion of the season (e.g. Jeff Samardzija 2014 had a
-- 3.14 ERA with Oakland -> does not match "Oakland + <= 3.00 ERA Season", even
-- though his combined ERA was 2.99). v_team_lookup resolves the display name.
SELECT b."playerID"
FROM {table} b
JOIN (
    SELECT t."yearID", t."teamID"
    FROM Teams t
    JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
    WHERE vl.name = %(c_team_name)s
) ft ON ft."yearID" = b."yearID" AND ft."teamID" = b."teamID"
GROUP BY b."playerID", b."yearID"
HAVING {rate} {op} %(c_value)s
