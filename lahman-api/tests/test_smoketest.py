"""Corpus-driven smoketest.

Runs every question from the scraped Immaculate Grid corpus through
engine.build() (pure Python, no DB round-trip) and reports which questions
classify successfully vs. which are unmatched.

Unmatched questions are SKIPPED (not failures) — some conditions in the corpus
(WAR, Negro League, etc.) are intentionally unsupported.

Run:
    uv run pytest tests/test_smoketest.py -v          # one line per question
    uv run pytest tests/test_smoketest.py -v --tb=no  # just pass/skip counts

The test ID includes game_id so you can trace any question back to its source
grid: e.g. test_smoketest[game_831-Detroit Tigers + Seattle Mariners]
"""
import json
from pathlib import Path

import pytest

from app import engine

_CORPUS = Path(__file__).parent / "corpus" / "all_grid_questions.json"


def _load_cases():
    data = json.loads(_CORPUS.read_text())
    seen = set()
    cases = []
    for game_id, questions in data.items():
        for question in questions:
            key = (game_id, question)
            if key not in seen:
                seen.add(key)
                cases.append((game_id, question))
    return cases


@pytest.mark.parametrize(
    "game_id,question",
    _load_cases(),
    ids=[f"game_{gid}-{q}" for gid, q in _load_cases()],
)
def test_smoketest(game_id, question):
    """Question must classify to a known category (not 'unmatched')."""
    _sql, _params, category = engine.build(question)

    if category == "unmatched":
        pytest.skip(f"unmatched: {question!r}")

    assert category != "error", f"engine error for {question!r}"
