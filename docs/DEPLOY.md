# Deployment & Operations

## Architecture

Two separate containers on the prod server (`66.179.136.39`):

| Container | Image | Managed by |
|---|---|---|
| `lahman-api-web-*` | `hurdbr/lahman-api` | Kamal (auto on `kamal deploy`) |
| `lahman-db-prod` | `hurdbr/lahman-db` | Manual — persistent, survives deploys |

The API container connects to Postgres at `172.17.0.1:5432` (Docker bridge gateway). The DB is not a Kamal accessory; `kamal remove` / `kamal deploy` does not touch it.

## Deploying a code change (API only)

```
kamal deploy
```

No DB involvement needed. The DB container keeps running.

## Migrating the database (new tables, new CSVs, schema changes)

When `lahman-db/init/` scripts or the CSV files change, the prod volume needs to be wiped and rebuilt from the new image. Postgres runs the init scripts only on a fresh (empty) data directory.

```
make push-db      # build for linux/amd64 and push to Docker Hub
make migrate-db   # wipe volume, pull new image, restart container
```

**What `migrate-db` does on the server:**
1. `docker rm -f lahman-db-prod` — stops and removes the old container
2. `docker volume rm lahman_pgdata_prod` — wipes the data directory
3. `docker pull hurdbr/lahman-db:latest` — pulls the new image
4. `docker run -d ... --restart unless-stopped` — starts fresh; postgres loads all CSVs (~2 min)

Check readiness:
```
kamal server exec "docker logs lahman-db-prod 2>&1 | tail -5"
```
Look for: `database system is ready to accept connections`

### Why `--platform linux/amd64`

The prod server is x86_64. Building locally on an Apple Silicon Mac produces an ARM64 image, which fails on the server with:
```
exec /usr/local/bin/docker-entrypoint.sh: exec format error
```
`push-db` always specifies `--platform linux/amd64` to avoid this.

## Checking prod status

```bash
kamal app logs          # API logs (alias defined in deploy.yml)
kamal server exec "docker ps -a"                        # all containers
kamal server exec "docker logs lahman-db-prod --tail 20 2>&1"  # DB logs
```

## DATABASE_URL

Set as a Kamal secret (not in the repo). Value is:
```
postgresql://postgres:lahman@172.17.0.1:5432/lahman
```
Re-inject if lost: `kamal env push` after updating `.env`.
