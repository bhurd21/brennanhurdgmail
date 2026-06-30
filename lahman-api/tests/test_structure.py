"""Structural quality checks that don't require known answers.

Runs a deterministic sample of questions and asserts:
  - Names are complete (2+ tokens, no NULL leakage).
  - Ranks are contiguous 1..N.
  - No duplicate players in one result.
  - >80% of the sample is answerable.
"""
import random

import pytest

SAMPLE_QUESTIONS = [
    "New York Yankees + Hall of Fame",
    "Boston Red Sox + Gold Glove",
    "300+ HR Career Batting + Hall of Fame",
    "All Star + Hall of Fame",
    "MVP + Gold Glove",
    "Silver Slugger + 300+ HR Career Batting",
    "Cy Young + Played Pitcher min. 1 game",
    "Cincinnati Reds + Chicago Cubs",
    "300+ HR Career Batting + 3000+ H Career Batting",
    "Played First Base min. 1 game + Hall of Fame",
    "Hall of Fame + Born Outside US 50 States and DC",
    "New York Yankees + 40+ HR Season Batting",
    "Boston Red Sox + Played First Base min. 1 game",
    "All Star + New York Yankees",
    "300+ HR Career Batting + Played First Base min. 1 game",
    "Hall of Fame + Only One Team",
    "World Series Champ WS Roster + Hall of Fame",
    "Los Angeles Dodgers + Hall of Fame",
    "Atlanta Braves + Hall of Fame",
    "San Francisco Giants + Hall of Fame",
]

# Shuffle with fixed seed for reproducibility.
_rng = random.Random(2025)
SAMPLE = _rng.sample(SAMPLE_QUESTIONS, len(SAMPLE_QUESTIONS))


@pytest.fixture(scope="module")
def results(run):
    return [(q, *run(q)) for q in SAMPLE]


def test_answerable_rate(results):
    answered = sum(1 for _, cat, players in results if cat != "unmatched" and len(players) > 0)
    rate = answered / len(results)
    assert rate >= 0.95, f"Only {answered}/{len(results)} questions answered ({rate:.0%})"


def test_names_are_complete(results):
    for question, category, players in results:
        if category == "unmatched":
            continue
        for p in players:
            name = p.get("name") or ""
            tokens = name.split()
            assert len(tokens) >= 2, (
                f"Incomplete name {name!r} in results for {question!r}"
            )


def test_ranks_are_contiguous(results):
    for question, category, players in results:
        if not players:
            continue
        ranks = [p["rank"] for p in players]
        assert ranks == list(range(1, len(ranks) + 1)), (
            f"Non-contiguous ranks for {question!r}: {ranks[:10]}"
        )


def test_no_duplicates(results):
    for question, category, players in results:
        ids = [p["bbref_id"] for p in players if p.get("bbref_id")]
        assert len(ids) == len(set(ids)), (
            f"Duplicate players in results for {question!r}"
        )
