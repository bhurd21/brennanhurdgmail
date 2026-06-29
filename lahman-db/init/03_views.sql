-- Lookup views: authoritative name → ID mappings that condition fragments join
-- against. Keeps team/award name resolution in SQL, out of Python.

-- v_team_lookup: every recognized display name → stable Lahman franchID.
-- Multiple names map to the same franchID for relocations and common aliases.
CREATE VIEW v_team_lookup AS
    SELECT 'Arizona Diamondbacks'               AS name, 'ARI' AS franch_id
UNION ALL SELECT 'Athletics'                   ,         'OAK'
UNION ALL SELECT 'Oakland Athletics'           ,         'OAK'
UNION ALL SELECT 'Atlanta Braves'              ,         'ATL'
UNION ALL SELECT 'Baltimore Orioles'           ,         'BAL'
UNION ALL SELECT 'Boston Red Sox'              ,         'BOS'
UNION ALL SELECT 'Chicago Cubs'                ,         'CHC'
UNION ALL SELECT 'Chicago White Sox'           ,         'CHW'
UNION ALL SELECT 'Cincinnati Reds'             ,         'CIN'
UNION ALL SELECT 'Cleveland Guardians'         ,         'CLE'
UNION ALL SELECT 'Colorado Rockies'            ,         'COL'
UNION ALL SELECT 'Detroit Tigers'              ,         'DET'
UNION ALL SELECT 'Houston Astros'              ,         'HOU'
UNION ALL SELECT 'Kansas City Royals'          ,         'KCR'
UNION ALL SELECT 'Los Angeles Angels'          ,         'ANA'
UNION ALL SELECT 'Los Angeles Angels of Anaheim',        'ANA'
UNION ALL SELECT 'Los Angeles Dodgers'         ,         'LAD'
UNION ALL SELECT 'Miami Marlins'               ,         'FLA'
UNION ALL SELECT 'Milwaukee Brewers'           ,         'MIL'
UNION ALL SELECT 'Minnesota Twins'             ,         'MIN'
UNION ALL SELECT 'New York Mets'               ,         'NYM'
UNION ALL SELECT 'New York Yankees'            ,         'NYY'
UNION ALL SELECT 'Philadelphia Phillies'       ,         'PHI'
UNION ALL SELECT 'Pittsburgh Pirates'          ,         'PIT'
UNION ALL SELECT 'San Diego Padres'            ,         'SDP'
UNION ALL SELECT 'San Francisco Giants'        ,         'SFG'
UNION ALL SELECT 'Seattle Mariners'            ,         'SEA'
UNION ALL SELECT 'St. Louis Cardinals'         ,         'STL'
UNION ALL SELECT 'Tampa Bay Rays'              ,         'TBD'
UNION ALL SELECT 'Texas Rangers'               ,         'TEX'
UNION ALL SELECT 'Toronto Blue Jays'           ,         'TOR'
UNION ALL SELECT 'Washington Nationals'        ,         'WSN';

-- v_award_lookup: display name → awardID as stored in AwardsPlayers.
-- "All Star" is absent intentionally — it lives in AllstarFull, not AwardsPlayers.
CREATE VIEW v_award_lookup AS
    SELECT 'Gold Glove'          AS name, 'Gold Glove'          AS award_id
UNION ALL SELECT 'Silver Slugger'      ,  'Silver Slugger'
UNION ALL SELECT 'MVP'                 ,  'Most Valuable Player'
UNION ALL SELECT 'Cy Young'            ,  'Cy Young Award'
UNION ALL SELECT 'Rookie of the Year'  ,  'Rookie of the Year';
