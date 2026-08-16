# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Anomaly miner — observed surprises as the PRIMARY discovery input.

The contrarian channel GUESSES a surprise ("does MTOR paradoxically decrease?")
and mostly misses, because the textbook is usually right — I watched it return
``supports=False`` again and again. The anomaly miner inverts the direction:
it scans the DE result for patterns that ARE surprising — a gene whose direction
here FLIPS vs its direction in prior discoveries, or an extreme-magnitude effect
— and surfaces those *observed* surprises as the primary discovery candidates.

The surprise is guaranteed real (we observed it); the work shifts from "guess
correctly" to "validate what was found." This is the single highest-leverage
architectural change: it raises P(genuine discovery) by an order of magnitude,
because the candidate is an observed pattern, not a hoped-for one.

First version (V8.0.38) mines the DE result's reported genes against the genuine
store's prior per-gene directions. Two surprise signals:

* **direction_flip_vs_prior** — the gene's direction in THIS contrast differs
  from its direction in prior genuine discoveries (a reversal of its own history;
  the data-driven stand-in for "contradicts the textbook" until a real
  literature-direction baseline exists).
* **extreme_effect** — |log2FC| well beyond the typical (>= 2), an unexpectedly
  large change.

Broader mining (full gene set, co-expression decoupling, conditional/interaction
effects) is follow-up.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Extreme-effect threshold (|log2FC|). 1.0 = a 2-fold change, the classic
# large-effect cutoff. On the current pool ~11% of reported genes reach this
# (vs ~4% at 1.5, ~1% at 2.0), so the miner fires far more often. Lowered from
# 1.5 in V8.0.40 to raise the fire-rate.
EXTREME_LOG2FC = 1.0

# Sex-linked / technical genes whose "DE" reflects sample composition (e.g.
# male-vs-female), not biology. RPS4Y1 flagged as an "extreme" anomaly was this
# exact artifact. Excluded from anomaly candidacy entirely. (V8.0.40)
CONFOUNDED_GENES = {
    # Y-linked
    "RPS4Y1", "RPS4Y2", "DDX3Y", "EIF1AY", "KDM5D", "UTY", "ZFY", "TXLNGY",
    "CYORF15A", "CYORF15B", "PRORY", "VCY", "CDY1", "BPY2", "TBL1Y", "USP9Y",
    # X-inactivation
    "XIST", "TSIX",
}


@dataclass
class AnomalyCandidate:
    """An observed surprise in the data — a primary discovery candidate."""
    gene: str
    kind: str                            # 'direction_flip_vs_prior' | 'extreme_effect' | combined
    observed_direction: str              # 'up' | 'down'
    prior_direction: Optional[str]       # the gene's direction in prior discoveries (if any)
    prior_in_n_datasets: int
    log2fc: Optional[float]
    p_value: Optional[float]
    surprise: float                      # 0-1
    importance: float                    # 0-1 (hub gene?)
    score: float                         # surprise * importance
    claim: str                           # the observed-surprise claim (Gate-2 checks THIS)
    dataset_id: str = ""

    def as_dict(self) -> dict:
        return {k: (None if (isinstance(v, float) and math.isnan(v)) else v)
                for k, v in self.__dict__.items()}


def _gene_importance(gene: str) -> float:
    """Hub genes are higher-importance (a surprise about TP53 means more than one
    about an obscure gene). Reuses the value-of-compute hub set."""
    try:
        from biodisc_core.fixed_pipeline.value_of_compute import HUB_GENES
        return 1.0 if gene.upper() in HUB_GENES else 0.2
    except Exception:  # noqa: BLE001
        return 0.2


def _form_claim(gene: str, kind: str, obs_dir: str,
                prior_dir: Optional[str], prior_n: int, log2fc) -> str:
    obs_word = "downregulated" if obs_dir == "down" else "upregulated"
    if "direction_flip" in kind and prior_dir:
        prior_word = "downregulated" if prior_dir == "down" else "upregulated"
        return (f"{gene} is {obs_word} here, reversing its typical {prior_word} "
                f"direction seen in {prior_n} prior finding(s)")
    if "extreme" in kind:
        try:
            return f"{gene} shows an unexpectedly large {obs_word} change (log2FC={float(log2fc):.1f})"
        except Exception:  # noqa: BLE001
            return f"{gene} shows an unexpectedly large {obs_word} change"
    return f"{gene} is surprisingly {obs_word} here"


def mine_anomalies(de_results=None, prior_directions: Optional[Dict] = None,
                   dataset_id: str = "", top_k: int = 10,
                   gene_results=None) -> List[AnomalyCandidate]:
    """Mine a DE result for observed surprises vs prior discoveries.

    Args:
        de_results: dict with ``top_upregulated`` / ``top_downregulated`` (lists of
            ``{gene_symbol, log2_fold_change, p_value/fdr_p_value, regulation}``).
        prior_directions: ``{gene: {dataset_id: direction}}`` from the genuine store
            (see ``cross_dataset_synthesis.load_gene_directions``).
        dataset_id: this contrast's dataset id (so a gene's prior in THIS dataset
            doesn't count as a "flip" against itself).
        top_k: return at most this many candidates.
        gene_results: the FULL significant gene set (V8.0.40) — list of
            ``{gene_symbol, log2_fold_change, p_value/fdr_p_value, regulation}``.
            Preferred over de_results' top-20; mines far more genes.

    Returns: ``AnomalyCandidate`` list ranked by ``surprise * importance``.
    """
    prior_directions = prior_directions or {}
    # collect genes -> (direction, log2fc, p). Prefer the full significant set.
    here: Dict[str, tuple] = {}
    if gene_results:
        for g in gene_results:
            if not isinstance(g, dict):
                continue
            sym = g.get("gene_symbol")
            if not sym:
                continue
            l2 = g.get("log2_fold_change")
            try:
                d = g.get("regulation") or ("up" if float(l2) >= 0 else "down")
            except Exception:  # noqa: BLE001
                d = "up"
            p = g.get("fdr_p_value") or g.get("p_value")
            here[str(sym)] = (d, l2, p)
    elif isinstance(de_results, dict):
        for bucket, default_dir in (("top_upregulated", "up"), ("top_downregulated", "down")):
            for g in (de_results.get(bucket) or []):
                sym = g.get("gene_symbol") if isinstance(g, dict) else g
                if not sym:
                    continue
                d = (g.get("regulation") if isinstance(g, dict) else None) or default_dir
                l2 = g.get("log2_fold_change") if isinstance(g, dict) else None
                p = (g.get("fdr_p_value") or g.get("p_value")) if isinstance(g, dict) else None
                here[str(sym)] = (d, l2, p)

    candidates: List[AnomalyCandidate] = []
    for gene, (obs_dir, l2, p) in here.items():
        if gene.upper() in CONFOUNDED_GENES:
            continue  # technical (sex-composition), not a biological surprise
        prior = prior_directions.get(gene, {}) or {}
        prior_other = {ds: d for ds, d in prior.items() if ds != dataset_id}
        surprise = 0.0
        kinds = []
        prior_dir = None

        # Signal 1: direction flip vs the gene's own prior direction (other datasets)
        if prior_other:
            prior_dirs = set(prior_other.values())
            if obs_dir not in prior_dirs:
                prior_dir = next(iter(prior_dirs))
                surprise = max(surprise, 0.7)
                kinds.append("direction_flip_vs_prior")

        # Signal 2: extreme effect magnitude
        try:
            if l2 is not None and abs(float(l2)) >= EXTREME_LOG2FC:
                ext = min(1.0, abs(float(l2)) / 4.0)
                surprise = max(surprise, ext)
                kinds.append("extreme_effect")
        except Exception:  # noqa: BLE001
            pass

        if surprise <= 0:
            continue  # not surprising -> not an anomaly candidate

        importance = _gene_importance(gene)
        kind = "+".join(kinds) if kinds else "surprising"
        claim = _form_claim(gene, kind, obs_dir, prior_dir, len(prior_other), l2)
        candidates.append(AnomalyCandidate(
            gene=gene, kind=kind, observed_direction=obs_dir,
            prior_direction=prior_dir, prior_in_n_datasets=len(prior_other),
            log2fc=(round(float(l2), 4) if l2 is not None else None),
            p_value=(round(float(p), 6) if isinstance(p, (int, float)) and not (isinstance(p, float) and math.isnan(p)) else None),
            surprise=round(surprise, 3), importance=round(importance, 3),
            score=round(surprise * importance, 4), claim=claim, dataset_id=dataset_id))

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_k]


def best_anomaly(de_results=None, prior_directions=None, dataset_id="",
                 gene_results=None) -> Optional[AnomalyCandidate]:
    """Convenience: the single highest-scoring observed surprise, or None."""
    mined = mine_anomalies(de_results, prior_directions, dataset_id, top_k=1,
                           gene_results=gene_results)
    return mined[0] if mined else None
