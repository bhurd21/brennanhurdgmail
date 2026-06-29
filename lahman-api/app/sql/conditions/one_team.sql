-- Played for exactly one franchise across an entire career.
SELECT a."playerID"
FROM Appearances a
JOIN Teams t USING ("yearID", "teamID")
GROUP BY a."playerID"
HAVING COUNT(DISTINCT t."franchID") = 1
