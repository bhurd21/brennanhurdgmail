-- Rate-stat threshold (AVG, ERA). {rate} is the computed expression.
-- {floor_clause} is the playing-time floor (e.g. AND SUM("AB") >= 200) so
-- cup-of-coffee players batting 1.000 don't flood the results. The engine
-- blanks it for sort=irrelevant, when surfacing those marginal players is the
-- whole point.
SELECT "playerID"
FROM {table}
GROUP BY {group}
HAVING {rate} {op} %({p}value)s
{floor_clause}
