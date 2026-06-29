-- Appeared in a major Negro League (Seamheads data added in Lahman 2024u).
-- lgID codes for Negro/independent major-caliber leagues per SABR recommendations.
SELECT DISTINCT "playerID"
FROM Appearances
WHERE "lgID" IN ('NAL','NNL','NN2','ECL','NSL','EWL','ANL','NAC','IND')
