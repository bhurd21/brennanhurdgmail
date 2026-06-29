-- Rate-stat threshold (AVG, ERA). {rate} is the computed expression.
SELECT "playerID"
FROM {table}
GROUP BY {group}
HAVING {rate} {op} %({p}value)s
