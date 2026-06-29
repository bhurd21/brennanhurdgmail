-- Award won in a season the player appeared for this team (grid rule).
-- Joins awardsplayers → appearances → Teams to tie yearID across all three.
SELECT DISTINCT ap."playerID"
FROM awardsplayers ap
JOIN v_award_lookup vl ON ap."awardID" = vl.award_id
JOIN appearances a     ON a."playerID" = ap."playerID" AND a."yearID" = ap."yearID"
JOIN Teams t           ON t."yearID"   = a."yearID"   AND t."teamID"  = a."teamID"
JOIN v_team_lookup vtl ON t."franchID" = vtl.franch_id
WHERE vl.name  = %(c_award_name)s
  AND vtl.name = %(c_team_name)s
