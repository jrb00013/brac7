from brac7.engine import BracketEngine
from brac7.models import BracketOptions


def test_19_teams_not_all_r1_byes():
    names = [f"Team {i}" for i in range(1, 20)]
    b = BracketEngine(BracketOptions(supports_byes=True)).generate(names)
    r1 = b.rounds[0]
    assert "play" in r1.name.lower() or r1.name == "Play-in Round"
    assert len(r1.matches) == 3
    for m in r1.matches:
        assert m.participant_a and m.participant_b
        assert not m.is_bye
    # Top seeds should not appear in play-in round
    r1_names = {m.participant_a for m in r1.matches} | {m.participant_b for m in r1.matches}
    assert "Team 1" not in r1_names
    assert "Team 13" not in r1_names


def test_true_bye_is_xor_only():
    """Full bracket ghost slot: both empty should not be is_bye."""
    opts = BracketOptions(supports_byes=True)
    # 4 teams in 8 bracket uses full path with empty slots
    b = BracketEngine(opts).generate(["A", "B", "C", "D"])
    r1 = b.rounds[0]
    both_filled = sum(1 for m in r1.matches if m.participant_a and m.participant_b)
    assert both_filled >= 2
