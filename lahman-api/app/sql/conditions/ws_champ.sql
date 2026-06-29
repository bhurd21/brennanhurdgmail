-- On the roster (appeared in a game) for a World Series-winning team.
SELECT DISTINCT a."playerID"
FROM Appearances a
JOIN Teams t USING ("yearID", "teamID")
WHERE t."WSWin" = 'Y'
