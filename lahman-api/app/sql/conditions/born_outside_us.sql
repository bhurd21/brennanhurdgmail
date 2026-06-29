-- Born outside the US 50 states + DC. USA birthCountry rows are exactly the
-- 50 states and DC; territories carry their own codes (P.R., V.I., ...).
SELECT "playerID"
FROM People
WHERE "birthCountry" IS DISTINCT FROM 'USA'
