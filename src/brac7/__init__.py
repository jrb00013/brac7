"""brac7 — tournament bracket generator (CLI, library, exports, UI)."""

from brac7.models import (
    Bracket,
    BracketOptions,
    MatchFormat,
    MatchNode,
    Participant,
    SeedingMode,
    TournamentFormat,
)
from brac7.engine import BracketEngine
from brac7.interactive import InteractiveState, create_interactive

__version__ = "0.2.0"
__all__ = [
    "Bracket",
    "BracketEngine",
    "BracketOptions",
    "MatchFormat",
    "MatchNode",
    "Participant",
    "SeedingMode",
    "TournamentFormat",
    "InteractiveState",
    "create_interactive",
    "__version__",
]
