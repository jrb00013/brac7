from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

from brac7.models import BracketOptions, Participant, SeedingMode


def next_power_of_two(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def standard_seed_order(size: int) -> list[int]:
    if size == 1:
        return [1]
    half = size // 2
    lower = standard_seed_order(half)
    upper = [size + 1 - s for s in lower]
    order: list[int] = []
    for a, b in zip(lower, upper):
        order.extend([a, b])
    return order


def assign_seeds(names: Sequence[str], options: BracketOptions) -> list[Participant]:
    ordered = list(names)
    if options.max_participants is not None:
        ordered = ordered[: options.max_participants]

    if options.seeding == SeedingMode.RANDOM:
        rng = random.Random(options.random_seed)
        rng.shuffle(ordered)

    return [Participant(name=n, seed=i + 1) for i, n in enumerate(ordered)]


@dataclass
class Slot:
    participant: Participant | None
    seed: int | None


def build_first_round_slots(participants: list[Participant], size: int) -> list[Slot]:
    by_seed = {p.seed: p for p in participants}
    slots: list[Slot] = []
    for seed_num in standard_seed_order(size):
        p = by_seed.get(seed_num)
        if p is None:
            slots.append(Slot(None, seed_num))
        else:
            slots.append(Slot(p, p.seed))
    return slots
