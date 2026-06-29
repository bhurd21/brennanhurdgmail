-- The one wrapper every question runs through.
--
-- The engine supplies the leading CTE block, which always ends by defining
-- matched_ids -- the qualifying set of "playerID"s. Usually that's two condition
-- fragments INTERSECTed; for a team + single-season stat it's one combined query
-- that ties the stat to the team (grid rule: a season stat must be achieved WITH
-- that team). Everything below decorates matched_ids: clean name, primary
-- position, career span, and a contiguous rank -- all in SQL.
--
-- Ranking: career games played DESC (relevant) / ASC (irrelevant), then last
-- season, then playerID. ROW_NUMBER uses {order}; final ORDER BY rank is fixed,
-- so rank stays a contiguous 1..N in display order.
WITH
{ctes}
appear_agg AS (
    SELECT a."playerID",
           SUM(a."G_all")  AS career_games,
           MAX(a."yearID") AS last_season,
           SUM(a."G_p")  AS gp,  SUM(a."G_c")  AS gc,  SUM(a."G_1b") AS g1,
           SUM(a."G_2b") AS g2,  SUM(a."G_3b") AS g3,  SUM(a."G_ss") AS gss,
           SUM(a."G_lf") AS glf, SUM(a."G_cf") AS gcf, SUM(a."G_rf") AS grf,
           SUM(a."G_dh") AS gdh
    FROM Appearances a
    JOIN matched_ids m USING ("playerID")
    GROUP BY a."playerID"
),
ranked AS (
    SELECT
        p."bbrefID"                                  AS bbref_id,
        btrim(p."nameFirst" || ' ' || p."nameLast")  AS name,
        CASE
            WHEN p."debut" IS NOT NULL AND p."finalGame" IS NOT NULL
            THEN EXTRACT(YEAR FROM p."debut")::int || '-' ||
                 EXTRACT(YEAR FROM p."finalGame")::int
        END                                          AS career,
        pos.position                                 AS position,
        COALESCE(aa.career_games, 0)                 AS career_games,
        aa.last_season                               AS last_season,
        p."playerID"                                 AS player_id
    FROM matched_ids m
    JOIN People p USING ("playerID")
    LEFT JOIN appear_agg aa USING ("playerID")
    -- Primary position = the position with the most games for this player.
    LEFT JOIN LATERAL (
        SELECT v.label AS position
        FROM (VALUES
            ('Pitcher',           aa.gp),
            ('Catcher',           aa.gc),
            ('First Base',        aa.g1),
            ('Second Base',       aa.g2),
            ('Third Base',        aa.g3),
            ('Shortstop',         aa.gss),
            ('Left Field',        aa.glf),
            ('Center Field',      aa.gcf),
            ('Right Field',       aa.grf),
            ('Designated Hitter', aa.gdh)
        ) AS v(label, games)
        WHERE v.games > 0
        ORDER BY v.games DESC
        LIMIT 1
    ) pos ON true
    -- Drop rows with missing name parts (kills "NULL Johnson").
    WHERE p."nameFirst" IS NOT NULL AND p."nameFirst" <> ''
      AND p."nameLast"  IS NOT NULL AND p."nameLast"  <> ''
)
SELECT
    -- {order} is set by the `sort` param: prominent-first (relevant) or
    -- obscure-first (irrelevant). The final ORDER BY rank below is unchanged,
    -- so rank stays a contiguous 1..N in display order either way.
    ROW_NUMBER() OVER ( ORDER BY {order} ) AS rank,
    name,
    position,
    career,
    bbref_id
FROM ranked
ORDER BY rank
LIMIT %(limit)s;
