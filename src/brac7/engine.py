from __future__ import annotations

import itertools

from brac7.models import (
    Bracket,
    BracketOptions,
    MatchFormat,
    MatchNode,
    Participant,
    Round,
    TournamentFormat,
)
from brac7.seeding import Slot, assign_seeds, build_first_round_slots, next_power_of_two


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
            if self.options.supports_byes and count < size:
                return self._single_elimination_with_top_byes(participants, size)
            return self._single_elimination_full(participants, size)
        if self.options.format == TournamentFormat.DOUBLE_ELIMINATION:
            return self._double_elimination(participants, size)
        return self._round_robin(participants)

    def _single_elimination_with_top_byes(
        self, participants: list[Participant], size: int
    ) -> Bracket:
        n = len(participants)
        num_byes = size - n
        bye_teams = participants[:num_byes]
        play_in = participants[num_byes:]

        bracket = Bracket(
            title=self.options.title,
            options=self.options,
            participants=participants,
            size=size,
        )
        rounds: list[Round] = []

        r1_matches: list[MatchNode] = []
        play_count = len(play_in)
        if play_count >= 2:
            for i in range(play_count // 2):
                a = play_in[i]
                b = play_in[play_count - 1 - i]
                node = MatchNode(
                    id=f"W-R1-M{i + 1}",
                    round_index=0,
                    match_index=i,
                    bracket="winners",
                    participant_a=a.name,
                    participant_b=b.name,
                    seed_a=a.seed,
                    seed_b=b.seed,
                    is_bye=False,
                )
                node.label = self._match_label(node, 1)
                r1_matches.append(node)

        if r1_matches:
            rounds.append(Round(0, self._round_name_for_play_in(len(r1_matches)), r1_matches))

        r2_team_count = size // 2
        current_matches = self._build_round_from_seeds(
            participants,
            num_byes,
            r1_matches,
            r2_team_count,
            round_num=2,
            round_index=1,
        )
        rounds.append(Round(1, self._round_name(0, r2_team_count), current_matches))
        round_idx = 2
        round_num = 3

        while len(current_matches) > 1:
            next_matches: list[MatchNode] = []
            for i in range(0, len(current_matches), 2):
                left, right = current_matches[i], current_matches[i + 1]
                match_idx = i // 2
                node = MatchNode(
                    id=f"W-R{round_num}-M{match_idx + 1}",
                    round_index=round_idx,
                    match_index=match_idx,
                    bracket="winners",
                    feeds_from=(left.id, right.id),
                )
                node.label = self._match_label(node, round_num)
                next_matches.append(node)
            rounds.append(
                Round(round_idx, self._round_name(round_idx, size // 2), next_matches)
            )
            current_matches = next_matches
            round_idx += 1
            round_num += 1

        bracket.rounds = rounds
        return bracket

    def _build_round_from_seeds(
        self,
        all_participants: list[Participant],
        num_byes: int,
        r1_matches: list[MatchNode],
        team_count: int,
        round_num: int,
        round_index: int,
    ) -> list[MatchNode]:
        from brac7.seeding import standard_seed_order

        by_seed = {p.seed: p for p in all_participants}
        pair_order: list[Slot] = []
        for seed_num in standard_seed_order(team_count):
            if seed_num <= num_byes:
                pair_order.append(Slot(by_seed.get(seed_num), seed_num))
            else:
                pair_order.append(Slot(None, seed_num))

        matches: list[MatchNode] = []
        r1_feed = {num_byes + 1 + i: m for i, m in enumerate(r1_matches)}

        for i in range(0, len(pair_order), 2):
            a, b = pair_order[i], pair_order[i + 1]
            match_idx = i // 2
            feeds: list[str] = []
            if a.participant is None and a.seed in r1_feed:
                feeds.append(r1_feed[a.seed].id)
            if b.participant is None and b.seed in r1_feed:
                feeds.append(r1_feed[b.seed].id)

            has_a = a.participant is not None
            has_b = b.participant is not None
            is_bye = (has_a ^ has_b) and self.options.supports_byes

            node = MatchNode(
                id=f"W-R{round_num}-M{match_idx + 1}",
                round_index=round_index,
                match_index=match_idx,
                bracket="winners",
                participant_a=a.participant.name if a.participant else None,
                participant_b=b.participant.name if b.participant else None,
                seed_a=a.seed if a.participant else a.seed,
                seed_b=b.seed if b.participant else b.seed,
                is_bye=is_bye,
                feeds_from=tuple(feeds),
            )
            node.label = self._match_label(node, round_num)
            matches.append(node)
        return matches

    def _single_elimination_full(self, participants: list[Participant], size: int) -> Bracket:
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
            has_a, has_b = a.participant is not None, b.participant is not None
            is_bye = (has_a ^ has_b) and self.options.supports_byes
            node = MatchNode(
                id=f"W-R1-M{match_idx + 1}",
                round_index=0,
                match_index=match_idx,
                bracket="winners",
                participant_a=a.participant.name if a.participant else None,
                participant_b=b.participant.name if b.participant else None,
                seed_a=a.seed if a.participant else None,
                seed_b=b.seed if b.participant else None,
                is_bye=is_bye,
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

    def _round_name_for_play_in(self, num_matches: int) -> str:
        if num_matches == 1:
            return "Play-in Final"
        return "Play-in Round"

    def _double_elimination(self, participants: list[Participant], size: int) -> Bracket:
        winners = (
            self._single_elimination_with_top_byes(participants, size)
            if self.options.supports_byes and len(participants) < size
            else self._single_elimination_full(participants, size)
        )
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
        return winners

    def _round_robin(self, participants: list[Participant]) -> Bracket:
        n = len(participants)
        bracket = Bracket(
            title=self.options.title,
            options=self.options,
            participants=participants,
            size=n,
        )
        rounds: list[Round] = []
        if n % 2 == 1:
            participants = participants + [Participant("BYE", seed=0)]
            n += 1

        num_rounds = n - 1
        num_matches = n // 2
        all_names = [p.name for p in participants]

        for rnd_idx in range(num_rounds):
            matches: list[MatchNode] = []
            for match_idx in range(num_matches):
                a = all_names[match_idx]
                b = all_names[n - 1 - match_idx]
                if "BYE" in (a, b):
                    continue
                pa = next(p for p in participants if p.name == a)
                pb = next(p for p in participants if p.name == b)
                node = MatchNode(
                    id=f"RR-R{rnd_idx + 1}-M{match_idx + 1}",
                    round_index=rnd_idx,
                    match_index=match_idx,
                    bracket="round_robin",
                    participant_a=a,
                    participant_b=b,
                    seed_a=pa.seed if pa.seed else None,
                    seed_b=pb.seed if pb.seed else None,
                )
                node.label = self._match_label(node, rnd_idx + 1)
                matches.append(node)

            rounds.append(
                Round(rnd_idx, f"Round {rnd_idx + 1}", matches)
            )

            all_names = (
                [all_names[0]]
                + [all_names[-1]]
                + all_names[1:-1]
            )

        bracket.rounds = rounds
        return bracket

    def _advance_byes(self, bracket: Bracket) -> None:
        if not self.options.supports_byes:
            return
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
        a = match.participant_a or self._empty_slot_label(match, "a")
        b = match.participant_b or self._empty_slot_label(match, "b")
        if fmt == MatchFormat.DETAILED:
            return f"{base} [{match.bracket}]: {a} vs {b}"
        return f"{base}: {a} vs {b}"

    def _empty_slot_label(self, match: MatchNode, side: str) -> str:
        if match.is_bye:
            return "BYE"
        return "TBD"
