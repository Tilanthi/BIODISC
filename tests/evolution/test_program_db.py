"""P1.3 + P2.1 — 2-D MAP-Elites archive + island model."""
from biodisc_core.evolution.program_db import (
    ProgramDatabase, IslandModel, method_family, _complexity,
)
from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore


def _score(agg, auroc=None, rep=None):
    return DEMethodScore(auroc=auroc or agg, replicate_concordance=rep or agg, aggregate=agg)


# --- method_family detection (behavioral descriptor 2) ---

def test_method_family_detection():
    assert method_family("def score(e,l):\n    return ttest_ind()") == "ttest"
    assert method_family("def score(e,l):\n    return mannwhitneyu()") == "rank"
    assert method_family("def score(e,l):\n    return e.mean(axis=1)") == "foldchange"
    assert method_family("def score(e,l):\n    return e.sum(axis=1)") == "other"


# --- 2-D MAP-Elites ---

def test_seed_addition_populates_archive():
    db = ProgramDatabase(n_buckets=8, seed=0)
    src = "def score(e, l):\n    return e.sum(axis=1)\n"
    added = db.add(src, _score(0.9), generation=0)
    assert added is not None
    assert len(db) == 1
    assert db.best().aggregate == 0.9


def test_higher_score_replaces_in_same_cell():
    # Two 'other'-family programs in the same complexity bucket -> same cell.
    db = ProgramDatabase(n_buckets=8, complexity_per_bucket=1000, seed=0)
    s1 = "def score(e, l):\n    return e.sum(axis=1)\n"
    s2 = "def score(e, l):\n    x = e.sum(axis=1)\n    return x\n"
    assert method_family(s1) == method_family(s2) == "other"
    db.add(s1, _score(0.7), generation=0)
    db.add(s2, _score(0.8), generation=1)
    assert db.best().aggregate == 0.8
    assert len(db) == 1  # same cell -> replaced, not added


def test_different_families_kept_as_separate_niches():
    # Same complexity bucket but different families -> two cells, both kept.
    db = ProgramDatabase(n_buckets=8, complexity_per_bucket=1000, seed=0)
    ttest_src = "def score(e, l):\n    return ttest_ind()\n"          # 'ttest'
    fc_src = "def score(e, l):\n    return e.mean(axis=1)\n"          # 'foldchange'
    assert method_family(ttest_src) != method_family(fc_src)
    db.add(ttest_src, _score(0.70), generation=0)
    db.add(fc_src, _score(0.75), generation=1)
    assert len(db) == 2  # distinct (bucket, family) niches preserved
    assert {c[1] for c in db.occupied_cells()} == {"ttest", "foldchange"}


def test_duplicate_source_is_deduped():
    db = ProgramDatabase(seed=0)
    src = "def score(e, l):\n    return e.sum(axis=1)\n"
    first = db.add(src, _score(0.9), generation=0)
    second = db.add(src, _score(0.95), generation=1)
    assert first is not None
    assert second is None
    assert len(db.all_programs()) == 1


def test_sample_returns_parent_and_inspirations():
    db = ProgramDatabase(n_buckets=8, complexity_per_bucket=5, max_inspirations=2, seed=1)
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


# --- Island model ---

def test_island_model_distributes_and_finds_global_best():
    im = IslandModel(n_islands=3, migration_interval=1000, complexity_per_bucket=1000, seed=0)
    # All 'other' family; same complexity bucket -> would collide in one cell
    # on a single archive, but islands split them.
    for i in range(5):
        src = f"def score(e, l):\n    x = e.sum(axis=1)\n    return x + {i}\n"
        im.add(src, _score(0.6 + 0.05 * i), generation=i)
    assert im.best() is not None
    assert im.best().aggregate == 0.8  # 0.6 + 0.05*4
    assert len(im.all_programs()) == 5


def test_island_model_migration_copies_elites():
    im = IslandModel(n_islands=3, migration_interval=1, complexity_per_bucket=1000, seed=0)
    # Add one strong program; migration should propagate it to other islands.
    strong = "def score(e, l):\n    return ttest_ind()\n"  # 'ttest' family
    im.add(strong, _score(0.9), generation=0)
    # Force several adds to trigger migrations.
    for i in range(1, 6):
        im.add(f"def score(e, l):\n    return e.sum(axis=1) + {i}\n", _score(0.5), generation=i)
    # The strong source should now appear on more than one island.
    islands_with_strong = sum(
        1 for isl in im.islands
        if any(p.source == strong for p in isl.all_programs())
    )
    assert islands_with_strong >= 2


def test_island_model_sample_works_when_populated():
    im = IslandModel(n_islands=2, complexity_per_bucket=1000, seed=0)
    im.add("def score(e, l):\n    return ttest_ind()\n", _score(0.7), generation=0)
    parent, inspirations = im.sample()
    assert parent.aggregate == 0.7
