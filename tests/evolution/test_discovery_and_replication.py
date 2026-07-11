"""P3.1 + P3.2 — discovery programs + replication-anchored fitness."""
import numpy as np
import pytest

from biodisc_core.evolution.discovery import (
    compile_discover_program, validate_discover_source, run_discover_program,
    get_seed_discovery_program, DiscoveryClaim,
)
from biodisc_core.evolution.replication import (
    make_replication_pair, replication_fitness, ReplicationScore,
)
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark


def test_seed_discovery_source_valid_and_compiles():
    src = get_seed_discovery_program()
    assert validate_discover_source(src)
    fn = compile_discover_program(src)
    case = make_de_benchmark(n_genes=100, n_samples=30, n_de=10, seed=0)
    claims = fn(case.expression, case.labels)
    assert len(claims) > 0
    assert set(claims[0].keys()) >= {"gene_index", "direction", "effect_size",
                                     "ci_low", "ci_high", "p_value"}


def test_run_discover_program_coerces_claims():
    fn = compile_discover_program(get_seed_discovery_program())
    case = make_de_benchmark(n_genes=100, n_samples=30, n_de=10, seed=1)
    result = run_discover_program(fn, case.expression, case.labels,
                                  gene_symbols=[f"G{i}" for i in range(100)],
                                  dataset_id="test")
    assert result.dataset_id == "test"
    assert all(isinstance(c, DiscoveryClaim) for c in result.claims)
    assert all(c.gene_symbol is not None for c in result.claims)
    # CI brackets the effect size.
    for c in result.claims:
        assert c.ci_low <= c.effect_size <= c.ci_high


def test_replication_pair_shares_truth_independent_draws():
    a, b = make_replication_pair(n_genes=200, n_samples=30, n_de=20, seed=1)
    assert a.truth_de_indices == b.truth_de_indices
    # Independent expression draws (different seeds -> different values).
    assert not np.allclose(a.expression, b.expression)


def test_seed_discovery_replicates_well_on_pair():
    """The seed discovery program's claims should replicate on the held-out cohort."""
    fn = compile_discover_program(get_seed_discovery_program())
    pair = make_replication_pair(n_genes=400, n_samples=30, n_de=40, seed=3,
                                 effect_size=1.2, noise="gaussian")
    score = replication_fitness(fn, pair)
    assert isinstance(score, ReplicationScore)
    assert score.n_claims > 0
    assert score.replication_rate > 0.6, (
        f"seed claims should replicate on independent cohort: {score.replication_rate}"
    )
    assert score.precision > 0.5, f"seed should mostly find true DE genes: {score.precision}"
    assert 0.0 <= score.aggregate <= 1.0


def test_to_method_score_maps_for_archive():
    rs = ReplicationScore(replication_rate=0.8, precision=0.7, n_claims=10, aggregate=0.77)
    ms = rs.to_method_score()
    assert ms.aggregate == 0.77
    assert ms.replicate_concordance == 0.8
    assert ms.auroc == 0.7
