-- Career WAR threshold (bWAR from Baseball Reference, top-1000 all time).
SELECT "playerID"
FROM CareerWar
WHERE "career_war" >= %({p}value)s
