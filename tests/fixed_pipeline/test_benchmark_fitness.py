"""P0.6 — Defect F: truth-known benchmark + scalar fitness h."""
import numpy as np
import pytest

from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import make_de_benchmark
from biodisc_core.fixed_pipeline.benchmark.de_fitness import (
    score_de_method,
    score_de_method_on_real,
)


def _perfect_method(expression, labels):
    # Cheats using the benchmark truth — a perfect method should score ~1.0.
    # Validated by being called with whichever case (primary or held-out) is passed.
    case_expression = expression
    # Recover truth from the data: DE genes have a control/treatment mean shift.
    treat = labels == 1
    ctrl = labels == 0
    diff = case_expression[:, treat].mean(axis=1) - case_expression[:, ctrl].mean(axis=1)
    return np.abs(diff)


def _random_method(expression, labels):
    rng = np.random.default_rng(42)
    return rng.random(expression.shape[0])


def test_benchmark_is_deterministic():
    a = make_de_benchmark(n_genes=100, n_samples=20, n_de=10, seed=7)
    b = make_de_benchmark(n_genes=100, n_samples=20, n_de=10, seed=7)
    assert a.seed == b.seed
    np.testing.assert_array_equal(a.expression, b.expression)
    assert a.truth_de_indices == b.truth_de_indices


def test_truth_de_genes_are_actually_de():
    case = make_de_benchmark(n_genes=200, n_samples=40, n_de=20, seed=1, effect_size=2.0)
    treat = case.labels == 1
    ctrl = case.labels == 0
    de_diffs = [
        abs(case.expression[i, treat].mean() - case.expression[i, ctrl].mean())
        for i in case.truth_de_indices
    ]
    non_de = set(range(case.n_genes)) - case.truth_de_indices
    non_de_diffs = [
        abs(case.expression[i, treat].mean() - case.expression[i, ctrl].mean())
        for i in list(non_de)[:50]
    ]
    assert np.mean(de_diffs) > np.mean(non_de_diffs)


def test_perfect_method_scores_high_random_scores_low():
    case = make_de_benchmark(n_genes=500, n_samples=40, n_de=50, seed=1)
    perf = score_de_method(_perfect_method, case)
    rand = score_de_method(_random_method, case)
    assert perf.auroc > 0.95
    assert rand.auroc < perf.auroc
    assert 0.0 <= rand.aggregate <= perf.aggregate <= 1.0


def test_aggregate_blends_auroc_and_replicate():
    case = make_de_benchmark(n_genes=500, n_samples=40, n_de=50, seed=1)
    perf = score_de_method(_perfect_method, case)
    expected = 0.6 * perf.auroc + 0.4 * perf.replicate_concordance
    assert abs(perf.aggregate - expected) < 1e-9


def test_crashing_method_scores_zero():
    def bad_method(expression, labels):
        raise RuntimeError("boom")
    case = make_de_benchmark(n_genes=100, n_samples=20, n_de=10, seed=1)
    score = score_de_method(bad_method, case)
    assert score.aggregate == 0.0


def test_wrong_length_output_scores_zero():
    def short_method(expression, labels):
        return np.zeros(expression.shape[0] - 1)
    case = make_de_benchmark(n_genes=100, n_samples=20, n_de=10, seed=1)
    assert score_de_method(short_method, case).aggregate == 0.0


def test_real_data_hook_is_not_implemented_yet():
    with pytest.raises(NotImplementedError):
        score_de_method_on_real(lambda: None, _random_method)
