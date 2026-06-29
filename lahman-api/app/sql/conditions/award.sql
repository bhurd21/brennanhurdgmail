-- Won a named award at least once. v_award_lookup resolves the display name
-- (e.g. "MVP") to the awardID stored in AwardsPlayers ("Most Valuable Player").
SELECT DISTINCT ap."playerID"
FROM AwardsPlayers ap
JOIN v_award_lookup vl ON ap."awardID" = vl.award_id
WHERE vl.name = %({p}award_name)s
