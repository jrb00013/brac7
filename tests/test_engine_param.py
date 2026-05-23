import pytest

from brac7.engine import BracketEngine
from brac7.models import BracketOptions, SeedingMode, TournamentFormat


@pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 16, 17, 32])
def test_single_elimination_various_sizes(n):
    names = [f"Team {i}" for i in range(n)]
    b = BracketEngine(BracketOptions(supports_byes=True)).generate(names)
    assert b.size >= n
    assert (b.size & (b.size - 1)) == 0


@pytest.mark.parametrize("n", [3, 7, 15])
def test_single_elimination_odd_sizes(n):
    names = [f"Team {i}" for i in range(n)]
    b = BracketEngine(BracketOptions(supports_byes=True)).generate(names)
    assert len(b.participants) == n
    assert b.size > n


@pytest.mark.parametrize("seed", [0, 1, 42, 999, 123456])
def test_random_seeding_deterministic_parity(seed):
    names = [f"P{i}" for i in range(8)]
    o1 = BracketOptions(seeding=SeedingMode.RANDOM, random_seed=seed)
    o2 = BracketOptions(seeding=SeedingMode.RANDOM, random_seed=seed)
    b1 = BracketEngine(o1).generate(names)
    b2 = BracketEngine(o2).generate(names)
    assert [p.name for p in b1.participants] == [p.name for p in b2.participants]


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
def test_round_robin_play_counts(n):
    names = [f"Player {i}" for i in range(n)]
    b = BracketEngine(
        BracketOptions(format=TournamentFormat.ROUND_ROBIN)
    ).generate(names)
    total_matches = sum(len(r.matches) for r in b.rounds)
    expected = n * (n - 1) // 2
    assert total_matches == expected


def test_round_robin_each_pair_once():
    names = ["A", "B", "C", "D"]
    b = BracketEngine(
        BracketOptions(format=TournamentFormat.ROUND_ROBIN)
    ).generate(names)
    pairs = set()
    for r in b.rounds:
        for m in r.matches:
            pair = (m.participant_a, m.participant_b)
            pairs.add(pair)
    assert len(pairs) == 6
    assert ("A", "B") in pairs
    assert ("A", "C") in pairs
    assert ("A", "D") in pairs
    assert ("B", "C") in pairs
    assert ("B", "D") in pairs
    assert ("C", "D") in pairs


def test_all_matches_have_valid_ids():
    b = BracketEngine(
        BracketOptions(title="ID Test")
    ).generate(["A", "B", "C", "D"])
    seen = set()
    for m in b.all_matches():
        assert m.id not in seen
        seen.add(m.id)


def test_no_byes_when_disabled():
    opts = BracketOptions(supports_byes=False)
    names = ["A", "B", "C", "D"]
    b = BracketEngine(opts).generate(names)
    for m in b.all_matches():
        assert not m.is_bye


def test_round_robin_round_count():
    names = [f"T{i}" for i in range(10)]
    b = BracketEngine(
        BracketOptions(format=TournamentFormat.ROUND_ROBIN)
    ).generate(names)
    assert len(b.rounds) == 9
