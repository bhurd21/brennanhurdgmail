-- Played for exactly one franchise across an entire career, OR only one AL/NL
-- franchise (allowing appearances in historical leagues like AA, PL, FL, UA, NA).
-- The official rule: "only one major league franchise, or only one AL/NL team."
SELECT a."playerID"
FROM Appearances a
JOIN Teams t USING ("yearID", "teamID")
GROUP BY a."playerID"
HAVING
    COUNT(DISTINCT t."franchID") = 1
    OR COUNT(DISTINCT CASE WHEN t."lgID" IN ('AL', 'NL') THEN t."franchID" END) = 1
