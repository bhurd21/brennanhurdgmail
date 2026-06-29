import os
import sys
from pathlib import Path

import psycopg
import pytest
from psycopg.rows import dict_row

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))   # lahman-api/ (for app)

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:lahman@localhost:5544/lahman"
)


@pytest.fixture(scope="session")
def conn():
    with psycopg.connect(DATABASE_URL) as c:
        yield c


@pytest.fixture(scope="session")
def run(conn):
    """run(question) -> (category, [player dicts]); composes SQL then executes."""
    from app import engine

    def _run(question: str, limit: int = 100, sort: str = "relevant"):
        sql, params, category = engine.build(question, limit, sort)
        if sql is None:
            return category, []
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return category, cur.fetchall()

    return _run
