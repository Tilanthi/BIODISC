"""Scalar fitness function ``h`` for differential-expression methods.

This is the AlphaEvolve-style automated evaluator for the DE-method discovery
problem (Phase 1+). Two scores, combined into one scalar:

* ``auroc`` — does the method rank truly-DE genes above non-DE genes on a
  truth-known benchmark?
* ``replicate_concordance`` — the method's AUROC on a HELD-OUT benchmark
  (independent truth + noise). This rewards methods that generalize rather
  than overfit a single draw. In-sample p-values are NOT rewarded directly;
  generalization is.

Per the plan's anti-pseudo-science rules, validation is a hard GATE elsewhere
(not part of this fitness); this fitness only measures method quality on
truth-known / held-out data.
"""
import logging
import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .truth_known_fixture import BenchmarkCase, make_de_benchmark

logger = logging.getLogger(__name__)

# A DE method takes (expression [genes x samples], labels [samples]) and returns
# a per-gene score where HIGHER means "more differentially expressed".
DEMethod = Callable[[np.ndarray, np.ndarray], np.ndarray]

HELD_OUT_SEED_OFFSET = 1000  # deterministic held-out seed derivation


@dataclass
class DEMethodScore:
    """Scalar fitness result for a DE method on a benchmark."""
    auroc: float
    replicate_concordance: float
    aggregate: float  # the scalar fitness h in [0, 1]


def _auroc(scores: np.ndarray, truth_indices: set, n_genes: int) -> float:
    """Area under ROC via the rank-sum (Mann-Whitney U) identity.

    ``scores[i]`` higher = more likely DE. ``truth_indices`` are the positives.
    Returns 0.5 for degenerate/all-tied cases.
    """
    if n_genes == 0 or len(truth_indices) == 0 or len(truth_indices) == n_genes:
        return 0.5

    finite = np.isfinite(scores)
    if not finite.all():
        scores = np.where(finite, scores, -np.inf)

    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(n_genes, dtype=float)
    ranks[order] = np.arange(1, n_genes + 1)

    truth_mask = np.zeros(n_genes, dtype=bool)
    truth_mask[list(truth_indices)] = True

    n_pos = int(truth_mask.sum())
    n_neg = n_genes - n_pos
    sum_pos_ranks = float(ranks[truth_mask].sum())
    return (sum_pos_ranks - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def score_de_method(
    method: DEMethod,
    case: BenchmarkCase,
    held_out_seed_offset: int = HELD_OUT_SEED_OFFSET,
) -> DEMethodScore:
    """Score a DE method on a truth-known benchmark + held-out replication.

    Args:
        method: callable (expression, labels) -> per-gene scores (higher = more DE).
        case: a BenchmarkCase from make_de_benchmark.
        held_out_seed_offset: seed offset for the held-out benchmark.

    Returns:
        DEMethodScore with aggregate in [0, 1]. Crashes/non-finite -> aggregate 0.0.
    """
    try:
        primary_scores = method(case.expression, case.labels)
        primary_scores = np.asarray(primary_scores, dtype=float).reshape(-1)
        if primary_scores.shape[0] != case.n_genes:
            return DEMethodScore(0.0, 0.0, 0.0)

        auroc = _auroc(primary_scores, case.truth_de_indices, case.n_genes)

        held_out = make_de_benchmark(
            n_genes=case.n_genes,
            n_samples=case.n_samples,
            n_de=case.n_de,
            seed=case.seed + held_out_seed_offset,
            effect_size=case.effect_size,
            noise=case.noise,
        )
        ho_scores = method(held_out.expression, held_out.labels)
        ho_scores = np.asarray(ho_scores, dtype=float).reshape(-1)
        replicate = (
            _auroc(ho_scores, held_out.truth_de_indices, case.n_genes)
            if ho_scores.shape[0] == case.n_genes
            else 0.0
        )

        if not (math.isfinite(auroc) and math.isfinite(replicate)):
            return DEMethodScore(0.0, 0.0, 0.0)

        aggregate = 0.6 * auroc + 0.4 * replicate
        return DEMethodScore(
            auroc=float(auroc),
            replicate_concordance=float(replicate),
            aggregate=float(aggregate),
        )
    except Exception as exc:  # a method that crashes scores zero
        logger.warning(f"   DE method crashed during scoring: {exc}")
        return DEMethodScore(0.0, 0.0, 0.0)


def score_de_method_on_real(case_loader: Callable[[], BenchmarkCase], method: DEMethod) -> DEMethodScore:
    """Score a DE method on a REAL held-out dataset (Phase 1+).

    ``case_loader`` returns a BenchmarkCase whose truth_de_indices come from
    curated real ground truth (e.g. known marker genes of a real case/control
    study). NotImplemented until Phase 1 wires real cached datasets.
    """
    raise NotImplementedError(
        "Real-data held-out scoring is implemented in Phase 1. "
        "Use score_de_method on truth-known benchmarks for now."
    )
