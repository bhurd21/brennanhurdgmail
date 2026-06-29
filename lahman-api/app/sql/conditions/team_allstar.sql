-- All-Star selection in a season the player appeared for this team (grid rule).
SELECT DISTINCT af."playerID"
FROM AllstarFull af
JOIN appearances a ON a."playerID" = af."playerID" AND a."yearID" = af."yearID"
JOIN Teams t       ON t."yearID"   = a."yearID"    AND t."teamID" = a."teamID"
JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
WHERE vl.name = %(c_team_name)s
