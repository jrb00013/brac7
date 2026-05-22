import pytest

from brac7.engine import BracketEngine
from brac7.models import BracketOptions, SeedingMode, TournamentFormat


def test_single_elimination_size():
    opts = BracketOptions(format=TournamentFormat.SINGLE_ELIMINATION, supports_byes=True)
    b = BracketEngine(opts).generate(["A", "B", "C", "D", "E"])
    assert b.size == 8
    assert len(b.participants) == 5
    assert len(b.rounds) == 3


def test_requires_two():
    with pytest.raises(ValueError):
        BracketEngine().generate(["solo"])


def test_random_seeding_deterministic():
    names = ["a", "b", "c", "d"]
    o1 = BracketOptions(seeding=SeedingMode.RANDOM, random_seed=42)
    o2 = BracketOptions(seeding=SeedingMode.RANDOM, random_seed=42)
    b1 = BracketEngine(o1).generate(names)
    b2 = BracketEngine(o2).generate(names)
    assert [p.name for p in b1.participants] == [p.name for p in b2.participants]
