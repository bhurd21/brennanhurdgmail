-- Born in a specific country (Lahman birthCountry code: USA, CAN, D.R., P.R.).
SELECT "playerID"
FROM People
WHERE "birthCountry" = %({p}country)s
