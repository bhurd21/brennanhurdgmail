"""Like hurdb's test_service_combinations.rb: one test per condition-type combo.

Each case verifies:
  1. The question classifies to the expected category.
  2. The query returns results (not empty).
  3. Specific well-known players appear in the result set.

This is the primary regression guard. If a player who should obviously appear
is missing, the query logic is wrong — not just structurally broken.

Run: uv run pytest tests/test_combinations.py -v
"""
import pytest

# (id, question, expected_category, required_bbref_ids)
CASES = [
    (
        "award_award",
        "MVP + Gold Glove",
        "award_award",
        ["bondsba01"],          # Barry Bonds: 8 MVPs, 8 Gold Gloves
    ),
    (
        "award_stat",
        "Silver Slugger + 300+ HR Career Batting",
        "award_stat",
        ["bondsba01"],          # Barry Bonds: Silver Sluggers + 762 HR
    ),
    (
        "award_team",
        "All Star + New York Yankees",
        "award_team",
        ["jeterde01"],          # Derek Jeter: 14 All Stars as a Yankee
    ),
    (
        "award_position",
        "Cy Young + Played Pitcher min. 1 game",
        "award_position",
        ["gibsobo01"],          # Bob Gibson: 2 Cy Youngs (bbrefID: gibsobo01)
    ),
    (
        "award_player",
        "All Star + Hall of Fame",
        "award_player",
        ["mayswi01"],           # Willie Mays: 24 All Stars + HOF (bbrefID: mayswi01)
    ),
    (
        "team_team",
        "Cincinnati Reds + Philadelphia Phillies",
        "team_team",
        ["rosepe01"],           # Pete Rose: 19 yrs Reds, 5 yrs Phillies
    ),
    (
        "team_stat_career",
        "New York Yankees + 300+ HR Career Batting",
        "stat_team",
        ["ruthba01"],           # Babe Ruth: 714 HR, career as a Yankee
    ),
    (
        "team_stat_season_combined",
        "New York Yankees + 40+ HR Season Batting",
        "stat_team",
        ["ruthba01"],           # Ruth had many 40+ HR seasons as a Yankee
    ),
    (
        "team_position",
        "Boston Red Sox + Played First Base min. 1 game",
        "position_team",
        ["foxxji01"],           # Jimmie Foxx: Red Sox 1B, HOF
    ),
    (
        "team_player",
        "New York Yankees + Hall of Fame",
        "player_team",
        ["ruthba01"],           # Babe Ruth: Yankee + HOF
    ),
    (
        "stat_stat",
        "300+ HR Career Batting + 3000+ HITS Career Batting",
        "stat_stat",
        ["aaronha01"],          # Hank Aaron: 755 HR + 3771 H
    ),
    (
        "stat_position",
        "300+ HR Career Batting + Played First Base min. 1 game",
        "position_stat",
        ["thomeji01"],          # Jim Thome: 612 HR, 1B
    ),
    (
        "stat_player",
        "300+ HR Career Batting + Hall of Fame",
        "player_stat",
        ["mayswi01"],           # Willie Mays: 660 HR + HOF (bbrefID: mayswi01)
    ),
    (
        "position_position",
        "Played First Base min. 1 game + Played Outfield min. 1 game",
        "position_position",
        ["musiast01"],          # Stan Musial: 1894 OF games + 1016 1B games
    ),
    (
        "position_player",
        "Played First Base min. 1 game + Hall of Fame",
        "player_position",
        ["gehrilo01"],          # Lou Gehrig: 1B + HOF
    ),
    (
        "player_player",
        "Hall of Fame + Born Outside US 50 States and DC",
        "player_player",
        ["clemero01"],          # Roberto Clemente: HOF + born in Puerto Rico
    ),
]


@pytest.mark.parametrize(
    "question,expected_category,required_ids",
    [(c[1], c[2], c[3]) for c in CASES],
    ids=[c[0] for c in CASES],
)
def test_combination(run, question, expected_category, required_ids):
    category, players = run(question)

    assert category == expected_category, (
        f"Wrong category for {question!r}: expected {expected_category!r}, got {category!r}"
    )
    assert len(players) > 0, f"No results for {question!r}"

    returned_ids = {p["bbref_id"] for p in players}
    for req_id in required_ids:
        assert req_id in returned_ids, (
            f"Expected {req_id!r} in results for {question!r}.\n"
            f"Got (first 5): {sorted(returned_ids)[:5]}"
        )
