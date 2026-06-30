# lahman-api

REST API that answers [Immaculate Grid](https://www.immaculategrid.com) cells using the [Lahman Baseball Database](http://www.seanlahman.com). Given a two-condition question like `"Boston Red Sox + Gold Glove"`, it returns a ranked list of qualifying players.

Used by the `im-grid-slvr-extension` Chrome extension.

## Quick start

```bash
docker compose up -d --build
curl "localhost:8000/answer?question=Washington+Nationals+%2B+300%2B+HR+Career+Batting"
```

The first build takes ~2 minutes while Postgres loads all CSVs. Check readiness:

```bash
curl localhost:8000/health   # {"ok": true} when ready
```

## API

### `GET /answer`

Returns players matching a two-condition question.

| Param | Type | Default | Description |
|---|---|---|---|
| `question` | string | required | Two conditions joined by ` + ` |
| `limit` | int | 100 | Max players returned (1–500) |
| `obscure` | bool | false | `true` = most obscure players first |

```bash
# Prominent players first (default)
curl "localhost:8000/answer?question=Boston+Red+Sox+%2B+Hall+of+Fame"

# Most obscure first
curl "localhost:8000/answer?question=Boston+Red+Sox+%2B+Hall+of+Fame&obscure=true"
```

Response:

```json
{
  "question": "Boston Red Sox + Hall of Fame",
  "category": "player_team",
  "count": 29,
  "players": [
    {"rank": 1, "name": "Ted Williams", "position": "LF", "career": "1939–1960", "bbref_id": "willite01"},
    ...
  ],
  "sql": "..."
}
```

Questions that can't be parsed return `"category": "unmatched"` with an empty player list.

Rate limit: 30 requests/minute per IP.

### `POST /answers`

Batch endpoint — up to 10 questions in one request.

```bash
curl -X POST localhost:8000/answers \
  -H "Content-Type: application/json" \
  -d '{"questions": ["Boston Red Sox + Hall of Fame", "MVP + Gold Glove"], "limit": 50}'
```

Returns a list of `AnswerResult` objects in the same order as the input.

Rate limit: 10 requests/minute per IP.

### `GET /help`

Returns the full supported condition vocabulary: all team names, award names, player flags, positions, and stat tokens.

```bash
curl localhost:8000/help
```

### `GET /health` / `GET /up`

`/health` runs a live DB ping. `/up` is a shallow check used by Kamal.

## Question format

Questions are two conditions joined by ` + `. The conditions can be:

- **Team**: `"Boston Red Sox"`, `"Athletics"`, `"Washington Nationals"` — any of the 30 current franchises (with relocations handled: Expos → Nationals, etc.)
- **Award**: `"Gold Glove"`, `"MVP"`, `"Cy Young"`, `"All Star"`, `"Silver Slugger"`, `"Rookie of the Year"`
- **Player flag**: `"Hall of Fame"`, `"Born Outside US 50 States and DC"`, `"Only One Team"`, `"World Series Champ WS Roster"`, `"Threw a No-Hitter"`, `"Played In Major Negro Lgs"`
- **Position**: `"Played First Base min. 1 game"`, `"Played Catcher min. 1 game"`, `"Pitched min. 1 game"`, etc.
- **Career stat**: `"300+ HR Career Batting"`, `"3000+ H Career Batting"`, `"200+ Wins Career Pitching"`, `"40+ WAR Career"`
- **Season stat**: `"40+ HR Season Batting"`, `"≤ 3.00 ERA Season"`, `".300+ AVG Season Batting"`, `"30+ HR / 30+ SB Season"`

`GET /help` returns the exact accepted strings for each category.

**Unsupported conditions** (Lahman doesn't have the data): `6+ WAR Season`, `First Round Draft Pick`. These return `"unmatched"`.

## Testing

The stack must be up (`docker compose up -d`) before running tests.

```bash
# Primary regression suite — 18 cases covering every condition-type combination
make test-combinations

# Full suite (takes ~8 min — hits the DB for every corpus question)
make test

# Interactive debug for a specific question
make debug
# Question: Boston Red Sox + Gold Glove
```

The full smoke test runs every question from 831 scraped Immaculate Grid games through the DB and asserts each classified question returns at least one player.

## Docs

- [`docs/DEPLOY.md`](docs/DEPLOY.md) — production deployment with Kamal
- [`docs/RULES.md`](docs/RULES.md) — official Immaculate Grid rules (reference)
- [`docs/IMPLEMENTATION_NOTES.md`](docs/IMPLEMENTATION_NOTES.md) — how rules map to SQL
