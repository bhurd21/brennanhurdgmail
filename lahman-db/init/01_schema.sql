-- Lahman Baseball Database 1871-2025 : Postgres schema
-- One table per CSV. Column names preserved exactly from the CSV headers
-- (quoted, so mixed-case and numeric-leading names like "2B"/"3B" are kept).
-- Primary keys on every table; foreign keys only where the data reliably
-- references (playerID->People, franchID->TeamsFranchises, schoolID->Schools).
-- Column ORDER in each table matches the CSV header order exactly, because
-- COPY ... (FORMAT csv, HEADER true) maps columns positionally.

BEGIN;

-- ---------------------------------------------------------------------------
-- Parent / reference tables (loaded first so FKs resolve)
-- ---------------------------------------------------------------------------

CREATE TABLE People (
    "id"            integer PRIMARY KEY,
    "playerID"      text UNIQUE NOT NULL,
    "birthYear"     integer,
    "birthMonth"    integer,
    "birthDay"      integer,
    "birthCity"     text,
    "birthCountry"  text,
    "birthState"    text,
    "deathYear"     integer,
    "deathMonth"    integer,
    "deathDay"      integer,
    "deathCountry"  text,
    "deathState"    text,
    "deathCity"     text,
    "nameFirst"     text,
    "nameLast"      text,
    "nameGiven"     text,
    "weight"        integer,
    "height"        integer,
    "bats"          text,
    "throws"        text,
    "debut"         date,
    "bbrefID"       text,
    "finalGame"     date,
    "retroID"       text
);

CREATE TABLE Schools (
    "schoolID"   text PRIMARY KEY,
    "name_full"  text,
    "city"       text,
    "state"      text,
    "country"    text
);

CREATE TABLE TeamsFranchises (
    "franchID"    text PRIMARY KEY,
    "franchName"  text,
    "active"      text,
    "NAassoc"     text
);

CREATE TABLE Parks (
    "id"         integer PRIMARY KEY,
    "parkalias"  text,
    "parkkey"    text UNIQUE,
    "parkname"   text,
    "city"       text,
    "state"      text,
    "country"    text
);

CREATE TABLE Teams (
    "yearID"          integer NOT NULL,
    "lgID"            text,
    "teamID"          text NOT NULL,
    "franchID"        text REFERENCES TeamsFranchises ("franchID"),
    "divID"           text,
    "Rank"            integer,
    "G"               integer,
    "Ghome"           integer,
    "W"               integer,
    "L"               integer,
    "DivWin"          text,
    "WCWin"           text,
    "LgWin"           text,
    "WSWin"           text,
    "R"               integer,
    "AB"              integer,
    "H"               integer,
    "2B"              integer,
    "3B"              integer,
    "HR"              integer,
    "BB"              integer,
    "SO"              integer,
    "SB"              integer,
    "CS"              integer,
    "HBP"             integer,
    "SF"              integer,
    "RA"              integer,
    "ER"              integer,
    "ERA"             numeric,
    "CG"              integer,
    "SHO"             integer,
    "SV"              integer,
    "IPouts"          integer,
    "HA"              integer,
    "HRA"             integer,
    "BBA"             integer,
    "SOA"             integer,
    "E"               integer,
    "DP"              integer,
    "FP"              numeric,
    "name"            text,
    "park"            text,
    "attendance"      integer,
    "BPF"             integer,
    "PPF"             integer,
    "teamIDBR"        text,
    "teamIDlahman45"  text,
    "teamIDretro"     text,
    PRIMARY KEY ("yearID", "teamID")
);

-- ---------------------------------------------------------------------------
-- Player statistics
-- ---------------------------------------------------------------------------

CREATE TABLE Batting (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "stint"     integer NOT NULL,
    "teamID"    text,
    "lgID"      text,
    "G"         integer,
    "AB"        integer,
    "R"         integer,
    "H"         integer,
    "2B"        integer,
    "3B"        integer,
    "HR"        integer,
    "RBI"       integer,
    "SB"        integer,
    "CS"        integer,
    "BB"        integer,
    "SO"        integer,
    "IBB"       integer,
    "HBP"       integer,
    "SH"        integer,
    "SF"        integer,
    "GIDP"      integer,
    PRIMARY KEY ("playerID", "yearID", "stint")
);

CREATE TABLE Pitching (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "stint"     integer NOT NULL,
    "teamID"    text,
    "lgID"      text,
    "W"         integer,
    "L"         integer,
    "G"         integer,
    "GS"        integer,
    "CG"        integer,
    "SHO"       integer,
    "SV"        integer,
    "IPouts"    integer,
    "H"         integer,
    "ER"        integer,
    "HR"        integer,
    "BB"        integer,
    "SO"        integer,
    "BAOpp"     numeric,
    "ERA"       numeric,
    "IBB"       integer,
    "WP"        integer,
    "HBP"       integer,
    "BK"        integer,
    "BFP"       integer,
    "GF"        integer,
    "R"         integer,
    "SH"        integer,
    "SF"        integer,
    "GIDP"      integer,
    PRIMARY KEY ("playerID", "yearID", "stint")
);

CREATE TABLE Fielding (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "stint"     integer NOT NULL,
    "teamID"    text,
    "lgID"      text,
    "POS"       text NOT NULL,
    "G"         integer,
    "GS"        integer,
    "InnOuts"   integer,
    "PO"        integer,
    "A"         integer,
    "E"         integer,
    "DP"        integer,
    "PB"        integer,
    "WP"        integer,
    "SB"        integer,
    "CS"        integer,
    "ZR"        numeric,
    PRIMARY KEY ("playerID", "yearID", "stint", "POS")
);

CREATE TABLE FieldingOF (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "stint"     integer NOT NULL,
    "Glf"       integer,
    "Gcf"       integer,
    "Grf"       integer,
    PRIMARY KEY ("playerID", "yearID", "stint")
);

CREATE TABLE FieldingOFsplit (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "stint"     integer NOT NULL,
    "teamID"    text,
    "lgID"      text,
    "POS"       text NOT NULL,
    "G"         integer,
    "GS"        integer,
    "InnOuts"   integer,
    "PO"        integer,
    "A"         integer,
    "E"         integer,
    "DP"        integer,
    "PB"        integer,
    "WP"        integer,
    "SB"        integer,
    "CS"        integer,
    "ZR"        numeric,
    PRIMARY KEY ("playerID", "yearID", "stint", "POS")
);

CREATE TABLE Appearances (
    "yearID"     integer NOT NULL,
    "teamID"     text NOT NULL,
    "lgID"       text,
    "playerID"   text NOT NULL REFERENCES People ("playerID"),
    "G_all"      integer,
    "GS"         integer,
    "G_batting"  integer,
    "G_defense"  integer,
    "G_p"        integer,
    "G_c"        integer,
    "G_1b"       integer,
    "G_2b"       integer,
    "G_3b"       integer,
    "G_ss"       integer,
    "G_lf"       integer,
    "G_cf"       integer,
    "G_rf"       integer,
    "G_of"       integer,
    "G_dh"       integer,
    "G_ph"       integer,
    "G_pr"       integer,
    PRIMARY KEY ("yearID", "teamID", "playerID")
);

CREATE TABLE Salaries (
    "yearID"    integer NOT NULL,
    "teamID"    text NOT NULL,
    "lgID"      text NOT NULL,
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "salary"    integer,
    PRIMARY KEY ("yearID", "teamID", "lgID", "playerID")
);

-- ---------------------------------------------------------------------------
-- Post-season statistics
-- ---------------------------------------------------------------------------

CREATE TABLE BattingPost (
    "yearID"    integer NOT NULL,
    "round"     text NOT NULL,
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "teamID"    text,
    "lgID"      text,
    "G"         integer,
    "AB"        integer,
    "R"         integer,
    "H"         integer,
    "2B"        integer,
    "3B"        integer,
    "HR"        integer,
    "RBI"       integer,
    "SB"        integer,
    "CS"        integer,
    "BB"        integer,
    "SO"        integer,
    "IBB"       integer,
    "HBP"       integer,
    "SH"        integer,
    "SF"        integer,
    "GIDP"      integer,
    PRIMARY KEY ("yearID", "round", "playerID")
);

CREATE TABLE PitchingPost (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "round"     text NOT NULL,
    "teamID"    text,
    "lgID"      text,
    "W"         integer,
    "L"         integer,
    "G"         integer,
    "GS"        integer,
    "CG"        integer,
    "SHO"       integer,
    "SV"        integer,
    "IPouts"    integer,
    "H"         integer,
    "ER"        integer,
    "HR"        integer,
    "BB"        integer,
    "SO"        integer,
    "BAOpp"     numeric,
    "ERA"       numeric,
    "IBB"       integer,
    "WP"        integer,
    "HBP"       integer,
    "BK"        integer,
    "BFP"       integer,
    "GF"        integer,
    "R"         integer,
    "SH"        integer,
    "SF"        integer,
    "GIDP"      integer,
    PRIMARY KEY ("playerID", "yearID", "round")
);

CREATE TABLE FieldingPost (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "teamID"    text,
    "lgID"      text,
    "round"     text NOT NULL,
    "POS"       text NOT NULL,
    "G"         integer,
    "GS"        integer,
    "InnOuts"   integer,
    "PO"        integer,
    "A"         integer,
    "E"         integer,
    "DP"        integer,
    "TP"        integer,
    "PB"        integer,
    "SB"        integer,
    "CS"        integer,
    PRIMARY KEY ("playerID", "yearID", "round", "POS")
);

CREATE TABLE SeriesPost (
    "yearID"        integer NOT NULL,
    "round"         text NOT NULL,
    "teamIDwinner"  text,
    "lgIDwinner"    text,
    "teamIDloser"   text,
    "lgIDloser"     text,
    "wins"          integer,
    "losses"        integer,
    "ties"          integer,
    PRIMARY KEY ("yearID", "round")
);

-- ---------------------------------------------------------------------------
-- Managers
-- ---------------------------------------------------------------------------

CREATE TABLE Managers (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "teamID"    text NOT NULL,
    "lgID"      text,
    "inseason"  integer NOT NULL,
    "G"         integer,
    "W"         integer,
    "L"         integer,
    "rank"      integer,
    "plyrMgr"   text,
    PRIMARY KEY ("playerID", "yearID", "teamID", "inseason")
);

CREATE TABLE ManagersHalf (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "yearID"    integer NOT NULL,
    "teamID"    text NOT NULL,
    "lgID"      text,
    "inseason"  integer NOT NULL,
    "half"      integer NOT NULL,
    "G"         integer,
    "W"         integer,
    "L"         integer,
    "rank"      integer,
    PRIMARY KEY ("playerID", "yearID", "teamID", "inseason", "half")
);

-- ---------------------------------------------------------------------------
-- Awards
-- ---------------------------------------------------------------------------

-- AwardsPlayers has repeating awards (e.g. Player of the Week) within the same
-- player/award/year/league, so it gets a surrogate identity primary key.
CREATE TABLE AwardsPlayers (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "awardID"   text NOT NULL,
    "yearID"    integer NOT NULL,
    "lgID"      text,
    "tie"       text,
    "notes"     text,
    "id"        bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY
);

CREATE TABLE AwardsManagers (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "awardID"   text NOT NULL,
    "yearID"    integer NOT NULL,
    "lgID"      text NOT NULL,
    "tie"       text,
    "notes"     text,
    PRIMARY KEY ("playerID", "awardID", "yearID", "lgID")
);

CREATE TABLE AwardsSharePlayers (
    "awardID"     text NOT NULL,
    "yearID"      integer NOT NULL,
    "lgID"        text NOT NULL,
    "playerID"    text NOT NULL REFERENCES People ("playerID"),
    "pointsWon"   numeric,
    "pointsMax"   integer,
    "votesFirst"  numeric,
    PRIMARY KEY ("awardID", "yearID", "lgID", "playerID")
);

CREATE TABLE AwardsShareManagers (
    "awardID"     text NOT NULL,
    "yearID"      integer NOT NULL,
    "lgID"        text NOT NULL,
    "playerID"    text NOT NULL REFERENCES People ("playerID"),
    "pointsWon"   numeric,
    "pointsMax"   integer,
    "votesFirst"  numeric,
    PRIMARY KEY ("awardID", "yearID", "lgID", "playerID")
);

-- ---------------------------------------------------------------------------
-- All-Star, Hall of Fame, College, Home games, Half-season standings
-- ---------------------------------------------------------------------------

-- AllstarFull can have duplicate (playerID, yearID, gameNum) rows (e.g. years
-- with no gameNum), so it gets a surrogate identity primary key.
CREATE TABLE AllstarFull (
    "playerID"     text NOT NULL REFERENCES People ("playerID"),
    "yearID"       integer NOT NULL,
    "gameNum"      integer,
    "gameID"       text,
    "teamID"       text,
    "lgID"         text,
    "GP"           integer,
    "startingPos"  text,   -- usually a position number, but Negro League rows use "9;9"
    "id"           bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY
);

CREATE TABLE HallOfFame (
    "playerID"     text NOT NULL REFERENCES People ("playerID"),
    "yearid"       integer NOT NULL,
    "votedBy"      text NOT NULL,
    "ballots"      integer,
    "needed"       integer,
    "votes"        integer,
    "inducted"     text,
    "category"     text,
    "needed_note"  text,
    PRIMARY KEY ("playerID", "yearid", "votedBy")
);

-- yearID is occasionally blank (Negro League records, year unknown) and
-- (playerID, schoolID) is not unique, so this table gets a surrogate PK.
CREATE TABLE CollegePlaying (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    "schoolID"  text NOT NULL REFERENCES Schools ("schoolID"),
    "yearID"    integer,
    "id"        bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY
);

CREATE TABLE HomeGames (
    "yearkey"     integer NOT NULL,
    "leaguekey"   text,
    "teamkey"     text NOT NULL,
    "parkkey"     text NOT NULL,
    "spanfirst"   date,
    "spanlast"    date,
    "games"       integer,
    "openings"    integer,
    "attendance"  integer,
    PRIMARY KEY ("yearkey", "teamkey", "parkkey")
);

CREATE TABLE TeamsHalf (
    "yearID"  integer NOT NULL,
    "lgID"    text,
    "teamID"  text NOT NULL,
    "Half"    integer NOT NULL,
    "divID"   text,
    "DivWin"  text,
    "Rank"    integer,
    "G"       integer,
    "W"       integer,
    "L"       integer,
    PRIMARY KEY ("yearID", "teamID", "Half")
);

-- ---------------------------------------------------------------------------
-- Supplemental / derived data
-- ---------------------------------------------------------------------------

CREATE TABLE NoHitters (
    "playerID"  text NOT NULL REFERENCES People ("playerID"),
    PRIMARY KEY ("playerID")
);

CREATE TABLE CareerWar (
    "playerID"   text    NOT NULL REFERENCES People ("playerID"),
    "career_war" numeric NOT NULL,
    PRIMARY KEY ("playerID")
);

COMMIT;
