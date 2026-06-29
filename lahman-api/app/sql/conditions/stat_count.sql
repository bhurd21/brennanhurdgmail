-- Counting-stat threshold (HR, Hits, RBI, K, Wins, Saves, ...).
-- {group} is "playerID" for a career total or "playerID", "yearID" for a
-- single season. {table}/{col}/{op} come from the trusted stat lookup.
SELECT "playerID"
FROM {table}
GROUP BY {group}
HAVING SUM("{col}") {op} %({p}value)s
