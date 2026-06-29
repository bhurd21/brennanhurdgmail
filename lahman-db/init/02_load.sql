-- Load every CSV into its table. Runs on first container boot only.
-- COPY is positional: it skips the header line and maps columns by order,
-- so the surrogate-id tables list their CSV columns explicitly.
-- Parents are loaded before children so foreign keys resolve.

\set ON_ERROR_STOP on
\set csv '/csv/'

-- Reference / parent tables
COPY People            FROM '/csv/People.csv'            WITH (FORMAT csv, HEADER true);
COPY Schools           FROM '/csv/Schools.csv'           WITH (FORMAT csv, HEADER true);
COPY TeamsFranchises   FROM '/csv/TeamsFranchises.csv'   WITH (FORMAT csv, HEADER true);
COPY Parks             FROM '/csv/Parks.csv'             WITH (FORMAT csv, HEADER true);
COPY Teams             FROM '/csv/Teams.csv'             WITH (FORMAT csv, HEADER true);

-- Player statistics
COPY Batting           FROM '/csv/Batting.csv'           WITH (FORMAT csv, HEADER true);
COPY Pitching          FROM '/csv/Pitching.csv'          WITH (FORMAT csv, HEADER true);
COPY Fielding          FROM '/csv/Fielding.csv'          WITH (FORMAT csv, HEADER true);
COPY FieldingOF        FROM '/csv/FieldingOF.csv'        WITH (FORMAT csv, HEADER true);
COPY FieldingOFsplit   FROM '/csv/FieldingOFsplit.csv'   WITH (FORMAT csv, HEADER true);
COPY Appearances       FROM '/csv/Appearances.csv'       WITH (FORMAT csv, HEADER true);
COPY Salaries          FROM '/csv/Salaries.csv'          WITH (FORMAT csv, HEADER true);

-- Post-season
COPY BattingPost       FROM '/csv/BattingPost.csv'       WITH (FORMAT csv, HEADER true);
COPY PitchingPost      FROM '/csv/PitchingPost.csv'      WITH (FORMAT csv, HEADER true);
COPY FieldingPost      FROM '/csv/FieldingPost.csv'      WITH (FORMAT csv, HEADER true);
COPY SeriesPost        FROM '/csv/SeriesPost.csv'        WITH (FORMAT csv, HEADER true);

-- Managers
COPY Managers          FROM '/csv/Managers.csv'          WITH (FORMAT csv, HEADER true);
COPY ManagersHalf      FROM '/csv/ManagersHalf.csv'      WITH (FORMAT csv, HEADER true);

-- Awards (AwardsPlayers has a surrogate id -> list CSV columns explicitly)
COPY AwardsPlayers ("playerID","awardID","yearID","lgID","tie","notes")
                       FROM '/csv/AwardsPlayers.csv'     WITH (FORMAT csv, HEADER true);
COPY AwardsManagers    FROM '/csv/AwardsManagers.csv'    WITH (FORMAT csv, HEADER true);
COPY AwardsSharePlayers  FROM '/csv/AwardsSharePlayers.csv'  WITH (FORMAT csv, HEADER true);
COPY AwardsShareManagers FROM '/csv/AwardsShareManagers.csv' WITH (FORMAT csv, HEADER true);

-- All-Star (surrogate id -> list CSV columns explicitly), HoF, College, etc.
COPY AllstarFull ("playerID","yearID","gameNum","gameID","teamID","lgID","GP","startingPos")
                       FROM '/csv/AllstarFull.csv'       WITH (FORMAT csv, HEADER true);
COPY HallOfFame        FROM '/csv/HallOfFame.csv'        WITH (FORMAT csv, HEADER true);
COPY CollegePlaying ("playerID","schoolID","yearID")
                       FROM '/csv/CollegePlaying.csv'    WITH (FORMAT csv, HEADER true);
COPY HomeGames         FROM '/csv/HomeGames.csv'         WITH (FORMAT csv, HEADER true);
COPY TeamsHalf         FROM '/csv/TeamsHalf.csv'         WITH (FORMAT csv, HEADER true);

-- Supplemental
COPY NoHitters         FROM '/csv/NoHitters.csv'         WITH (FORMAT csv, HEADER true);
