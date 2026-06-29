-- Players who appeared for a franchise (any of its historical team IDs).
-- v_team_lookup resolves the display name to a stable franchID, so relocations
-- and renames (Expos->Nationals, Marlins, A's...) all match correctly.
SELECT DISTINCT a."playerID"
FROM Appearances a
JOIN Teams t USING ("yearID", "teamID")
JOIN v_team_lookup vl ON t."franchID" = vl.franch_id
WHERE vl.name = %({p}team_name)s
