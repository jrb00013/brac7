"""Bracket generation engine — single and double elimination."""

from __future__ import annotations

from brac7.models import (
    Bracket,
    BracketOptions,
    MatchFormat,
    MatchNode,
    Participant,
    Round,
    TournamentFormat,
)
from brac7.seeding import assign_seeds, build_first_round_slots, next_power_of_two


class BracketEngine:
    def __init__(self, options: BracketOptions | None = None):
        self.options = options or BracketOptions()

    def generate(self, names: list[str]) -> Bracket:
        participants = assign_seeds(names, self.options)
        count = len(participants)
        if count < 2:
            raise ValueError("Need at least 2 participants")

        size = next_power_of_two(count)
        if not self.options.supports_byes and count != size:
            raise ValueError(
                f"{count} participants requires byes to fill bracket size {size}; "
                "enable supports_byes or adjust max_participants"
            )

        if self.options.format == TournamentFormat.SINGLE_ELIMINATION:
            return self._single_elimination(participants, size)
        return self._double_elimination(participants, size)

    def _single_elimination(self, participants: list[Participant], size: int) -> Bracket:
        bracket = Bracket(
            title=self.options.title,
            options=self.options,
            participants=participants,
            size=size,
        )
        slots = build_first_round_slots(participants, size)
        rounds: list[Round] = []
        current_matches: list[MatchNode] = []

        for i in range(0, len(slots), 2):
            a, b = slots[i], slots[i + 1]
            match_idx = i // 2
            is_bye = a.participant is None or b.participant is None
            node = MatchNode(
                id=f"W-R1-M{match_idx + 1}",
                round_index=0,
                match_index=match_idx,
                bracket="winners",
                participant_a=a.participant.name if a.participant else None,
                participant_b=b.participant.name if b.participant else None,
                seed_a=a.seed if a.participant else a.seed,
                seed_b=b.seed if b.participant else b.seed,
                is_bye=is_bye and self.options.supports_byes,
            )
            node.label = self._match_label(node, 1)
            current_matches.append(node)

        round_num = 1
        rounds.append(Round(0, self._round_name(0, size), current_matches))

        while len(current_matches) > 1:
            next_matches: list[MatchNode] = []
            for i in range(0, len(current_matches), 2):
                left, right = current_matches[i], current_matches[i + 1]
                match_idx = i // 2
                node = MatchNode(
                    id=f"W-R{round_num + 1}-M{match_idx + 1}",
                    round_index=round_num,
                    match_index=match_idx,
                    bracket="winners",
                    feeds_from=(left.id, right.id),
                )
                node.label = self._match_label(node, round_num + 1)
                next_matches.append(node)
            rounds.append(Round(round_num, self._round_name(round_num, size), next_matches))
            current_matches = next_matches
            round_num += 1

        bracket.rounds = rounds
        self._advance_byes(bracket)
        return bracket

    def _double_elimination(self, participants: list[Participant], size: int) -> Bracket:
        """Winners bracket + placeholder losers bracket structure."""
        winners = self._single_elimination(participants, size)
        losers_round = Round(
            index=len(winners.rounds),
            name="Losers Bracket (placeholder)",
            matches=[
                MatchNode(
                    id="L-R1-M1",
                    round_index=len(winners.rounds),
                    match_index=0,
                    bracket="losers",
                    label="Losers flow — assign after winners R1",
                )
            ],
        )
        winners.rounds.append(losers_round)
        winners.options = self.options
        return winners

    def _advance_byes(self, bracket: Bracket) -> None:
        """Propagate bye winners into next-round slots (display only)."""
        if not self.options.supports_byes:
            return
        by_id = {m.id: m for m in bracket.all_matches()}
        for rnd in bracket.rounds:
            for m in rnd.matches:
                if not m.is_bye:
                    continue
                winner = m.participant_a or m.participant_b
                if not winner:
                    continue
                for nxt in bracket.all_matches():
                    if m.id not in nxt.feeds_from:
                        continue
                    if nxt.participant_a is None:
                        nxt.participant_a = winner
                    elif nxt.participant_b is None:
                        nxt.participant_b = winner

    def _round_name(self, index: int, size: int) -> str:
        remaining = size // (2 ** (index + 1))
        if remaining == 1:
            return "Final"
        if remaining == 2:
            return "Semifinals"
        if remaining == 4:
            return "Quarterfinals"
        return f"Round {index + 1}"

    def _match_label(self, match: MatchNode, round_number: int) -> str:
        fmt = self.options.match_format
        base = f"R{round_number}-M{match.match_index + 1}"
        if fmt == MatchFormat.COMPACT:
            return base
        a = match.participant_a or ("BYE" if match.is_bye else "TBD")
        b = match.participant_b or ("BYE" if match.is_bye else "TBD")
        if fmt == MatchFormat.DETAILED:
            return f"{base} [{match.bracket}]: {a} vs {b}"
        return f"{base}: {a} vs {b}"
