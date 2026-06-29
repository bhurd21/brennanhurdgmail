#!/usr/bin/env python3
"""Interactive debug tool for a single question.

Like hurdb's debug_service.rb: shows the full pipeline for one question
(split → classify → SQL → results) so failures are easy to pinpoint.

Usage (from lahman-api-v2/lahman-api/):
    uv run python scripts/debug_question.py "Silver Slugger + 300+ HR Career Batting"

DATABASE_URL defaults to localhost:5544 (docker-compose dev stack).
Override: DATABASE_URL=postgresql://... uv run python scripts/debug_question.py "..."
"""
import os
import sys
from pathlib import Path

# Make `app` importable when run from scripts/ or lahman-api/
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg
from psycopg.rows import dict_row

from app import classifiers, engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:lahman@localhost:5544/lahman"
)

SEP = "─" * 70


def show_condition(label: str, text: str, cond):
    print(f"\nClassifying {label}: {text!r}")
    if cond is None:
        print(f"  -> UNMATCHED (no classifier recognised this)")
        return
    print(f"  -> category : {cond.category}")
    print(f"  -> fragment : {cond.fragment}.sql")
    if cond.fields:
        print(f"  -> fields   : {cond.fields}")
    print(f"  -> params   : {cond.params}")


def main(question: str):
    print(f"\n{SEP}")
    print(f"Question: {question}")
    print(SEP)

    parts = [p.strip() for p in question.strip().split(" + ")]
    if len(parts) != 2:
        print("ERROR: question must have exactly two conditions separated by ' + '")
        sys.exit(1)

    print(f"\nSplit:")
    print(f"  A: {parts[0]!r}")
    print(f"  B: {parts[1]!r}")

    cond_a = classifiers.classify(parts[0])
    cond_b = classifiers.classify(parts[1])

    show_condition("A", parts[0], cond_a)
    show_condition("B", parts[1], cond_b)

    if cond_a is None or cond_b is None:
        print(f"\n{SEP}")
        print("Cannot continue: one or both conditions are unmatched.")
        sys.exit(0)

    sql, params, category = engine.build(question, limit=10)

    print(f"\nCategory: {category!r}")
    if category in ("stat_team", "team_stat"):
        stat_cond = cond_b if cond_a.category == "team" else cond_a
        path = "combined_ctes (season stat tied to team)" if engine._is_season_stat(stat_cond) \
               else "normal_ctes (career stat, plain INTERSECT)"
    else:
        path = "normal_ctes (plain INTERSECT)"
    print(f"Path    : {path}")

    print(f"\n{SEP}")
    print("SQL:")
    print(SEP)
    print(sql)
    print(f"\nParams: {params}")
    print(SEP)

    print("\nExecuting...")
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"\nResults ({len(rows)} shown, limit=10):")
    for row in rows:
        rank = row.get("rank", "?")
        name = row.get("name", "?")
        pos = (row.get("position") or "-")[:15]
        career = row.get("career") or "-"
        bbref = row.get("bbref_id") or "-"
        print(f"  {rank:>3}. {name:<26} | {pos:<15} | {career:<10} | {bbref}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} \"Condition A + Condition B\"")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))
