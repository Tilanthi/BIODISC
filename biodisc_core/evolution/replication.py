"""Phase 3 — replication-anchored fitness for discovery programs.

THE ANCHOR (anti-pseudoscience rule #2): a claim made on a discovery cohort
must REPLICATE on an independent cohort. A discovery program that overfits
cohort A (e.g. p-hacks noise) will not replicate on cohort B, so selection on
replication_rate resists the failure mode evolutionary pressure would otherwise
create. Ground truth is used ONLY for a precision diagnostic — the program
itself never sees it.

make_replication_pair() produces two BenchmarkCases that SHARE the same truly-DE
genes but have independent expression draws (two independent cohorts of the same
study). This is truth-known BENCHMARK data used to score programs, not discovery
data (see the benchmark package docstring).
"""
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy import stats

from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark
from biodisc_core.fixed_pipeline.benchmark.de_fitness import DEMethodScore
from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import BenchmarkCase

from .discovery import run_discover_program


@dataclass
class ReplicationScore:
    replication_rate: float   # THE anchor: fraction of claims that replicate on cohort B
    precision: float          # diagnostic: fraction of claims that are truly DE
    n_claims: int
    aggregate: float = 0.0    # 0.7*replication + 0.3*precision (replication-dominant)

    def to_method_score(self) -> DEMethodScore:
        """Map onto DEMethodScore so the Phase 1-2 archive can store discovery programs.

        auroc<-precision, replicate_concordance<-replication_rate, aggregate<-aggregate.
        """
        return DEMethodScore(
            auroc=self.precision,
            replicate_concordance=self.replication_rate,
            aggregate=self.aggregate,
        )


def make_replication_pair(
    n_genes: int = 400,
    n_samples: int = 30,
    n_de: int = 40,
    seed: int = 1,
    effect_size: float = 1.0,
    noise: str = "gaussian",
) -> Tuple[BenchmarkCase, BenchmarkCase]:
    """Two cohorts with SHARED DE truth but independent expression draws."""
    rng = np.random.default_rng(seed)
    truth = rng.choice(n_genes, size=n_de, replace=False)
    a = make_de_benchmark(
        n_genes=n_genes, n_samples=n_samples, n_de=n_de,
        seed=seed * 2 + 1, effect_size=effect_size, noise=noise,
        truth_indices=truth,
    )
    b = make_de_benchmark(
        n_genes=n_genes, n_samples=n_samples, n_de=n_de,
        seed=seed * 2 + 2, effect_size=effect_size, noise=noise,
        truth_indices=truth,
    )
    assert a.truth_de_indices == b.truth_de_indices, "cohorts must share truth"
    return a, b


def _effect_and_p(expression, labels, gene_index):
    treat = labels == 1
    ctrl = labels == 0
    a = expression[gene_index, treat]
    b = expression[gene_index, ctrl]
    eff = float(a.mean() - b.mean())
    try:
        _, p = stats.ttest_ind(a, b)
        p = float(p) if p == p else 1.0
    except Exception:
        p = 1.0
    return eff, p


def replication_fitness(discover_fn, pair, p_threshold: float = 0.05) -> ReplicationScore:
    """Score a discovery program by how well its cohort-A claims replicate on B.

    A claim replicates on B if gene i has the SAME direction AND is significant
    (p < p_threshold) in cohort B. replication_rate = fraction replicated.
    precision (diagnostic) = fraction of claimed genes that are truly DE.
    """
    cohort_a, cohort_b = pair
    result = run_discover_program(
        discover_fn, cohort_a.expression, cohort_a.labels, dataset_id="cohort_a",
    )
    claims = result.claims
    n = len(claims)
    if n == 0:
        return ReplicationScore(0.0, 0.0, 0, 0.0)

    truth = cohort_a.truth_de_indices
    replicated = 0
    correct = 0
    for c in claims:
        eff_b, p_b = _effect_and_p(cohort_b.expression, cohort_b.labels, c.gene_index)
        if np.sign(eff_b) == c.direction and p_b < p_threshold:
            replicated += 1
        if c.gene_index in truth:
            correct += 1

    replication_rate = replicated / n
    precision = correct / n
    aggregate = 0.7 * replication_rate + 0.3 * precision
    return ReplicationScore(replication_rate, precision, n, aggregate)
