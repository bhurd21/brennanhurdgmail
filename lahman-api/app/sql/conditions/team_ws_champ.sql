-- World Series Champ tied to a specific team: player appeared for that team
-- in the season it won the World Series.
SELECT DISTINCT a."playerID"
FROM Appearances a
JOIN Teams t USING ("yearID", "teamID")
JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
WHERE vl.name = %(c_team_name)s
  AND t."WSWin" = 'Y'
