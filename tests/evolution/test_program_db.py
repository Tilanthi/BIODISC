"""P1.3 — MAP-Elites program database."""
from biodisc_core.evolution.program_db import ProgramDatabase, _complexity
from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore


def _score(agg, auroc=None, rep=None):
    return DEMethodScore(auroc=auroc or agg, replicate_concordance=rep or agg, aggregate=agg)


def test_seed_addition_populates_archive():
    db = ProgramDatabase(n_buckets=8, seed=0)
    src = "def score(e, l):\n    return e.sum(axis=1)\n"  # low complexity
    added = db.add(src, _score(0.9), generation=0)
    assert added is not None
    assert len(db) == 1
    assert db.best().aggregate == 0.9


def test_higher_score_replaces_in_same_bucket():
    db = ProgramDatabase(n_buckets=8, complexity_per_bucket=1000, seed=0)
    # Both programs fall in bucket 0 (complexity < 1000).
    s1 = "def score(e, l):\n    return e.sum(axis=1)\n"
    s2 = "def score(e, l):\n    return e.mean(axis=1)\n"
    db.add(s1, _score(0.7), generation=0)
    db.add(s2, _score(0.8), generation=1)
    # Best overall is the higher-scoring one; only one occupied bucket.
    assert db.best().aggregate == 0.8
    assert len(db) == 1


def test_duplicate_source_is_deduped():
    db = ProgramDatabase(seed=0)
    src = "def score(e, l):\n    return e.sum(axis=1)\n"
    first = db.add(src, _score(0.9), generation=0)
    second = db.add(src, _score(0.95), generation=1)
    assert first is not None
    assert second is None  # exact-duplicate source declined
    assert len(db.all_programs()) == 1


def test_sample_returns_parent_and_inspirations():
    db = ProgramDatabase(n_buckets=8, complexity_per_bucket=5, max_inspirations=2, seed=1)
    # Distinct complexities -> distinct buckets.
    progs = [
        "def score(e, l):\n    a = e.sum(axis=1)\n    b = a + 1\n    c = b * 2\n    return c\n",
        "def score(e, l):\n    return e.sum(axis=1)\n",
    ]
    for i, p in enumerate(progs):
        db.add(p, _score(0.8 + 0.01 * i), generation=i)
    assert len(db) >= 2
    parent, inspirations = db.sample()
    assert parent.source in progs
    assert all(ins.program_id != parent.program_id for ins in inspirations)


def test_complexity_descriptor_is_positive():
    assert _complexity("def score(e, l):\n    return e\n") > 0
