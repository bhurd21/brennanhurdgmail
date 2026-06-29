"""Async Postgres access. Read-only; one shared connection pool."""
import os

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:lahman@localhost:5432/lahman"
)

pool = AsyncConnectionPool(DATABASE_URL, open=False, min_size=1, max_size=10)


async def fetch(sql: str, params: dict) -> list[dict]:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(sql, params)
            return await cur.fetchall()


async def ping() -> bool:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            return (await cur.fetchone())[0] == 1
