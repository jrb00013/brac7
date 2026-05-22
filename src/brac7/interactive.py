"""Interactive bracket state — record winners and advance rounds."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from brac7.engine import BracketEngine
from brac7.models import Bracket, BracketOptions, MatchNode


@dataclass
class InteractiveState:
    """Serializable bracket session for UI and library consumers."""

    bracket_title: str
    options: dict
    participants: list[dict]
    match_results: dict[str, Optional[str]] = field(default_factory=dict)
    """match_id -> winner name"""

    @classmethod
    def from_bracket(cls, bracket: Bracket) -> InteractiveState:
        return cls(
            bracket_title=bracket.title,
            options={
                "format": bracket.options.format.value,
                "seeding": bracket.options.seeding.value,
                "supports_byes": bracket.options.supports_byes,
                "max_participants": bracket.options.max_participants,
                "match_format": bracket.options.match_format.value,
                "title": bracket.options.title,
                "random_seed": bracket.options.random_seed,
            },
            participants=[{"name": p.name, "seed": p.seed} for p in bracket.participants],
            match_results={m.id: None for m in bracket.all_matches()},
        )

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> InteractiveState:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    def set_winner(self, match_id: str, winner: str) -> None:
        if match_id not in self.match_results:
            raise KeyError(f"Unknown match: {match_id}")
        self.match_results[match_id] = winner

    def apply_results(self, bracket: Bracket) -> Bracket:
        """Return a copy of bracket tree with winners advanced to feeder matches."""
        by_id = {m.id: m for m in bracket.all_matches()}
        for match_id, winner in self.match_results.items():
            if not winner:
                continue
            match = by_id.get(match_id)
            if not match:
                continue
            for nxt in bracket.all_matches():
                if match_id not in nxt.feeds_from:
                    continue
                if nxt.participant_a is None:
                    nxt.participant_a = winner
                elif nxt.participant_b is None:
                    nxt.participant_b = winner
        return bracket


def create_interactive(names: list[str], options: BracketOptions | None = None) -> tuple[Bracket, InteractiveState]:
    bracket = BracketEngine(options).generate(names)
    return bracket, InteractiveState.from_bracket(bracket)
