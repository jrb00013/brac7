from brac7.seeding import assign_seeds, build_first_round_slots, next_power_of_two, standard_seed_order
from brac7.models import BracketOptions, SeedingMode


def test_next_power_of_two():
    assert next_power_of_two(1) == 1
    assert next_power_of_two(2) == 2
    assert next_power_of_two(3) == 4
    assert next_power_of_two(5) == 8
    assert next_power_of_two(16) == 16
    assert next_power_of_two(17) == 32


def test_standard_seed_order_size_2():
    assert standard_seed_order(2) == [1, 2]


def test_standard_seed_order_size_4():
    assert standard_seed_order(4) == [1, 4, 3, 2]


def test_standard_seed_order_size_8():
    assert standard_seed_order(8) == [1, 8, 5, 4, 3, 6, 7, 2]


def test_assign_seeds_preserves_order():
    names = ["Alpha", "Beta", "Gamma", "Delta"]
    opts = BracketOptions(seeding=SeedingMode.SEEDED)
    parts = assign_seeds(names, opts)
    assert [p.name for p in parts] == names
    assert [p.seed for p in parts] == [1, 2, 3, 4]


def test_assign_seeds_random_deterministic():
    names = ["a", "b", "c", "d", "e", "f"]
    o1 = BracketOptions(seeding=SeedingMode.RANDOM, random_seed=42)
    o2 = BracketOptions(seeding=SeedingMode.RANDOM, random_seed=42)
    assert [p.name for p in assign_seeds(names, o1)] == [p.name for p in assign_seeds(names, o2)]


def test_assign_seeds_respects_max():
    names = ["a", "b", "c", "d", "e", "f", "g", "h"]
    opts = BracketOptions(max_participants=4)
    parts = assign_seeds(names, opts)
    assert len(parts) == 4


def test_build_first_round_slots_4_teams():
    from brac7.seeding import Participant
    parts = [Participant("A", 1), Participant("B", 2), Participant("C", 3), Participant("D", 4)]
    slots = build_first_round_slots(parts, 4)
    assert len(slots) == 4


def test_build_first_round_slots_partial():
    from brac7.seeding import Participant
    parts = [Participant("A", 1), Participant("B", 2)]
    slots = build_first_round_slots(parts, 4)
    assert len(slots) == 4
    none_slots = sum(1 for s in slots if s.participant is None)
    assert none_slots == 2
