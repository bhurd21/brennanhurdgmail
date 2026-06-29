-- Position tied to a specific team: player appeared at that position in a game
-- for this team. {col} is an Appearances game-count column (G_ss, G_p, etc.).
SELECT DISTINCT a."playerID"
FROM Appearances a
JOIN Teams t USING ("yearID", "teamID")
JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
WHERE vl.name = %(c_team_name)s
  AND a."{col}" > 0
