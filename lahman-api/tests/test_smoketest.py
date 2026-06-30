"""Corpus-driven smoketest.

Runs every question from the scraped Immaculate Grid corpus through the full
pipeline (classify → SQL → DB execution) and asserts that each classified
question returns at least one player.

Unmatched questions are SKIPPED (not failures) — some conditions in the corpus
(WAR, Negro League, etc.) are intentionally unsupported.

Requires the stack to be up (make up).

Run:
    uv run pytest tests/test_smoketest.py -v          # one line per question
    uv run pytest tests/test_smoketest.py -v --tb=no  # just pass/skip counts

The test ID includes game_id so you can trace any question back to its source
grid: e.g. test_smoketest[game_831-Detroit Tigers + Seattle Mariners]
"""
import json
from pathlib import Path

import pytest

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
def test_smoketest(run, game_id, question):
    """Classified questions must return at least one player from the DB."""
    category, players = run(question)

    if category == "unmatched":
        pytest.skip(f"unmatched: {question!r}")

    assert category != "error", f"engine error for {question!r}"
    assert len(players) > 0, f"empty result set for classified question {question!r}"
