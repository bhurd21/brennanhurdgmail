-- Played at least one game at a position. {col} is an Appearances game-count
-- column (G_ss, G_p, ...) from the trusted position lookup.
SELECT DISTINCT "playerID"
FROM Appearances
WHERE "{col}" > 0
