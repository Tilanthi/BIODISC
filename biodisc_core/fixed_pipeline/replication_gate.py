"""Held-out replication anchor for the live discovery loop.

The flagging gate (``discovery_gate.py``) already refuses ``is_genuine=True``
unless ``report['replication']['replicated']`` is set — but nothing in the live
loop ever SET it, so every real-loop finding was stuck at
``candidate_unconfirmed``. This module produces that signal.

It implements the BIODISC analogue of ASTRA's train/test (leakage) discipline
(§7.3): the HEADLINE statistic must come from HELD-OUT data, not the same
samples used to find the effect. Concretely, a dataset's samples are split
stratified-by-group into a discovery split (60%) and a held-out split (40%);
the differential-expression analysis is re-run on each; a discovery-split
finding "replicates" iff its top genes are also significant (FDR<0.05) AND
same-direction in the held-out split above a minimum fraction.

HONEST SCOPE: this is INTERNAL held-out replication within one dataset —
stronger than single-pass significance, weaker than independent-cohort
replication (the gold standard). Genuine-tier findings are therefore
"internally replicated", not "independently replicated". Datasets too small to
split remain ``candidate_unconfirmed`` (no overclaiming).
"""
import hashlib
import logging
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ReplicationVerdict:
    replicated: bool
    replication_fraction: float
    n_replicated: int
    n_tested: int
    discovery_n_samples: int
    heldout_n_samples: int
    method: str
    reason: str


def _sample_axis(expression_data: np.ndarray, group_labels) -> int:
    """Return the axis along which samples lie (0 or 1), inferred from label count."""
    n = len(group_labels)
    if expression_data.shape[1] == n:
        return 1
    if expression_data.shape[0] == n:
        return 0
    # default: assume genes x samples
    return 1


def _stratified_split(groups: List, frac: float, seed: int) -> Tuple[List[int], List[int]]:
    """Split sample indices into discovery / held-out, stratified by group."""
    rng = np.random.default_rng(seed)
    by_group = {}
    for idx, g in enumerate(groups):
        by_group.setdefault(g, []).append(idx)
    discovery, heldout = [], []
    for g, idxs in by_group.items():
        idxs = list(idxs)
        rng.shuffle(idxs)
        # ensure each split keeps >=2 of this group when possible
        cut = max(2, int(round(len(idxs) * frac)))
        cut = min(cut, len(idxs) - 2) if len(idxs) > 4 else min(cut, len(idxs) - 1)
        cut = max(1, cut)
        discovery.extend(idxs[:cut])
        heldout.extend(idxs[cut:])
    return sorted(discovery), sorted(heldout)


def _slice(expression_data: np.ndarray, idxs: List[int], axis: int) -> np.ndarray:
    if axis == 1:
        return expression_data[:, idxs]
    return expression_data[idxs, :]


class ReplicationGate:
    """Internal held-out replication for single-cohort discoveries."""

    def __init__(
        self,
        top_n: int = 15,
        min_fraction: float = 0.40,
        min_replicated: int = 3,
        min_samples_for_split: int = 8,
        discovery_frac: float = 0.6,
    ):
        self.top_n = top_n
        self.min_fraction = min_fraction
        self.min_replicated = min_replicated
        self.min_samples_for_split = min_samples_for_split
        self.discovery_frac = discovery_frac

    def assess(
        self,
        expression_data: np.ndarray,
        gene_symbols: List[str],
        group_labels,
        analyze_fn: Callable,
        question: str = "",
        dataset_id: str = "",
    ) -> ReplicationVerdict:
        """Run discovery + held-out DE and test whether top genes replicate.

        ``analyze_fn(expression_data, gene_symbols, group_labels, question, dataset_id)``
        must return an object with ``.results`` (items exposing ``.gene_symbol``,
        ``.significant`` bool, ``.fdr_p_value`` float, ``.log2_fold_change`` float).
        """
        n_samples = len(group_labels)
        method = "internal_held_out_split"

        # Not enough samples to split honestly -> cannot establish replication.
        if n_samples < self.min_samples_for_split:
            return ReplicationVerdict(
                False, 0.0, 0, 0, n_samples, 0, method,
                f"too few samples to split ({n_samples}<{self.min_samples_for_split}); "
                "remains single-cohort candidate",
            )

        groups = list(group_labels)
        n_distinct = len(set(groups))
        if n_distinct < 2:
            return ReplicationVerdict(
                False, 0.0, 0, 0, n_samples, 0, method,
                "fewer than 2 groups; cannot contrast",
            )

        # Deterministic per-dataset seed (reproducible split).
        seed = int(hashlib.md5(str(dataset_id).encode("utf-8")).hexdigest()[:8], 16)
        disc_idx, held_idx = _stratified_split(groups, self.discovery_frac, seed)
        if len(disc_idx) < 4 or len(held_idx) < 4:
            return ReplicationVerdict(
                False, 0.0, 0, 0, len(disc_idx), len(held_idx), method,
                "split too unbalanced after stratification",
            )

        axis = _sample_axis(expression_data, group_labels)
        disc_X = _slice(expression_data, disc_idx, axis)
        held_X = _slice(expression_data, held_idx, axis)
        # Pass labels to the DE analyzer as an ndarray. The analyzer does
        # np.where(group_labels == 0), which only compares element-wise on an
        # array; a Python list makes `list == 0` scalar-False -> np.where(False)
        # -> 'nonzero on 0d' ValueError on every split — the bug that kept
        # replication at 0% and blocked every discovery from the genuine tier.
        arr = np.asarray(group_labels)
        disc_labels = arr[disc_idx]
        held_labels = arr[held_idx]

        # Each split DE is run independently; a failure on either split means
        # replication cannot be established (the discovery stays a candidate).
        # We catch per-split so a degenerate split degrades gracefully instead
        # of propagating (e.g. numpy "nonzero on 0d" on an edge-case split).
        try:
            disc_de = analyze_fn(disc_X, gene_symbols, disc_labels, question, dataset_id)
        except Exception as e:  # noqa: BLE001
            logger.warning("replication: discovery-split DE failed: %s", e)
            return ReplicationVerdict(
                False, 0.0, 0, 0, len(disc_idx), len(held_idx), method,
                f"discovery-split DE failed ({type(e).__name__}); not replicated",
            )
        try:
            held_de = analyze_fn(held_X, gene_symbols, held_labels, question, dataset_id)
        except Exception as e:  # noqa: BLE001
            logger.warning("replication: held-out-split DE failed: %s", e)
            return ReplicationVerdict(
                False, 0.0, 0, 0, len(disc_idx), len(held_idx), method,
                f"held-out-split DE failed ({type(e).__name__}); not replicated",
            )

        # Discovery top genes: most significant (lowest FDR) among significant ones.
        disc_sig = [r for r in disc_de.results if getattr(r, "significant", False)]
        disc_sig.sort(key=lambda r: getattr(r, "fdr_p_value", float("inf")))
        top = disc_sig[: self.top_n]
        if not top:
            return ReplicationVerdict(
                False, 0.0, 0, 0, len(disc_idx), len(held_idx), method,
                "no significant genes in discovery split",
            )

        held_by_gene = {r.gene_symbol: r for r in held_de.results}
        replicated = 0
        for r in top:
            h = held_by_gene.get(r.gene_symbol)
            if h is None:
                continue
            h_sig = getattr(h, "significant", False)
            same_dir = np.sign(getattr(r, "log2_fold_change", 0.0)) == np.sign(getattr(h, "log2_fold_change", 0.0))
            if h_sig and same_dir:
                replicated += 1

        frac = replicated / len(top)
        is_replicated = (replicated >= self.min_replicated) and (frac >= self.min_fraction)
        reason = (
            f"{replicated}/{len(top)} top discovery genes significant+same-direction in held-out "
            f"(fraction {frac:.2f})"
        )
        logger.info("🧬 replication gate: %s", reason)
        return ReplicationVerdict(
            is_replicated, round(frac, 4), replicated, len(top),
            len(disc_idx), len(held_idx), method, reason,
        )


def to_report_dict(verdict: ReplicationVerdict) -> dict:
    """Shape a verdict for ``report['replication']`` (consumed by discovery_gate)."""
    return {
        "replicated": bool(verdict.replicated),
        "replication_fraction": verdict.replication_fraction,
        "n_replicated": verdict.n_replicated,
        "n_tested": verdict.n_tested,
        "discovery_n_samples": verdict.discovery_n_samples,
        "heldout_n_samples": verdict.heldout_n_samples,
        "method": verdict.method,
        "reason": verdict.reason,
    }


def create_replication_gate(**kwargs) -> ReplicationGate:
    return ReplicationGate(**kwargs)


__all__ = [
    "ReplicationGate", "ReplicationVerdict", "to_report_dict", "create_replication_gate",
]
