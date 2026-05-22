"""Domain models and bracket configuration — source of truth for all exporters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TournamentFormat(str, Enum):
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"


class SeedingMode(str, Enum):
    RANDOM = "random"
    SEEDED = "seeded"


class MatchFormat(str, Enum):
    """How match slots are labeled in exports."""

    STANDARD = "standard"  # "R1-M3: Seed 4 vs Seed 12"
    COMPACT = "compact"  # "R1-M3"
    DETAILED = "detailed"  # includes bracket path + bye markers


@dataclass(frozen=True)
class BracketOptions:
    """Canonical options — PDF, XLSX, Mermaid, CLI, and UI all read this."""

    format: TournamentFormat = TournamentFormat.SINGLE_ELIMINATION
    seeding: SeedingMode = SeedingMode.SEEDED
    supports_byes: bool = True
    max_participants: Optional[int] = None
    match_format: MatchFormat = MatchFormat.STANDARD
    title: str = "Tournament Bracket"
    random_seed: Optional[int] = None

    def normalized_max(self, entrant_count: int) -> int:
        if self.max_participants is None:
            return entrant_count
        return min(self.max_participants, entrant_count)


@dataclass
class Participant:
    name: str
    seed: int


@dataclass
class MatchNode:
    """One match slot in the bracket tree."""

    id: str
    round_index: int
    match_index: int
    bracket: str  # "winners" | "losers" for double elim
    participant_a: Optional[str] = None
    participant_b: Optional[str] = None
    seed_a: Optional[int] = None
    seed_b: Optional[int] = None
    is_bye: bool = False
    feeds_from: tuple[str, ...] = ()
    label: str = ""

    def display_slot(self, side: str, options: BracketOptions) -> str:
        name = self.participant_a if side == "a" else self.participant_b
        seed = self.seed_a if side == "a" else self.seed_b
        if name is None:
            # BYE = empty slot in a 1v0 auto-advance only; not "everyone vs ghost seed"
            other = self.participant_b if side == "a" else self.participant_a
            if self.is_bye and other:
                return "BYE"
            return "TBD"
        if options.match_format == MatchFormat.COMPACT:
            return name
        if options.match_format == MatchFormat.DETAILED and seed is not None:
            return f"({seed}) {name}"
        if seed is not None and options.seeding == SeedingMode.SEEDED:
            return f"{name} [#{seed}]"
        return name


@dataclass
class Round:
    index: int
    name: str
    matches: list[MatchNode] = field(default_factory=list)


@dataclass
class Bracket:
    title: str
    options: BracketOptions
    participants: list[Participant]
    rounds: list[Round] = field(default_factory=list)
    size: int = 0  # bracket capacity (power of 2)

    @property
    def format_label(self) -> str:
        return self.options.format.value.replace("_", " ").title()

    def all_matches(self) -> list[MatchNode]:
        out: list[MatchNode] = []
        for r in self.rounds:
            out.extend(r.matches)
        return out
