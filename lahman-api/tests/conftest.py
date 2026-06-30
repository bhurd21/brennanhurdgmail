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

    def _run(question: str, limit: int = 100, obscure: bool = False):
        sql, params, category = engine.build(question, limit, obscure)
        if sql is None:
            return category, []
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, params)
                return category, cur.fetchall()
        except Exception:
            conn.rollback()
            raise

    return _run
