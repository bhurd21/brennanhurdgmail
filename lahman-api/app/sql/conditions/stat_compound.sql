-- Two simultaneous counting thresholds in one timeframe,
-- e.g. "30+ HR / 30+ SB Season Batting".
SELECT "playerID"
FROM {table}
GROUP BY {group}
HAVING SUM("{col1}") >= %({p}v1)s
   AND SUM("{col2}") >= %({p}v2)s
