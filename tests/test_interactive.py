from brac7.interactive import create_interactive
from brac7.models import BracketOptions


def test_interactive_winner():
    bracket, state = create_interactive(["A", "B", "C", "D"], BracketOptions())
    first = bracket.rounds[0].matches[0]
    state.set_winner(first.id, "A")
    assert state.match_results[first.id] == "A"
