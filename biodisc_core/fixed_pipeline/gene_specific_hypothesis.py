"""Gene-specific hypothesis testing — the keystone of the surprise-seeking rebuild.

The default DE primitive returns the dominant top-N signal in a contrast
(proliferation in tumors, metabolism in liver) — which is, by construction, the
textbook signal the field already found. It physically cannot answer a specific
question like *"does MTOR paradoxically DECREASE in liver cancer?"*; it reports
ANLN/MAD2L1 and stamps whatever comes out. That is why contrarian findings
reached 'genuine' with an unrelated generic signature.

This module tests the **named gene's** specific direction and significance
directly, so a funded contrarian bet can actually deliver a surprise:

    test_gene_hypothesis(expr, genes, labels, "MTOR", claimed_direction="down")
      -> HypothesisResult(observed_direction=..., supports_claim=...)

* ``supports_claim=True``  — the named gene is significant in the CONTRARIAN
  direction the question asserted. That is a genuine surprise candidate.
* ``supports_claim=False`` — the textbook held (or the gene isn't significant).
  The contrarian bet failed; downgrade, don't stamp genuine on the framing alone.
* ``claimed_direction=None`` — the question asserts a *relative* direction
  ("opposite", "reversed") that can't be resolved without a textbook baseline.
  Inconclusive; see the anomaly_vs_expectation scaffold (a research item).

This reuses the existing expression matrix + labels — no new data path — and is
pure / offline-testable.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np

logger = logging.getLogger(__name__)

_DIRECTION_UP = ("increase", "increases", "increased", "upregulat", "higher",
                 "elevated", "overexpress", "induc", "activat", "raise", "gain")
_DIRECTION_DOWN = ("decrease", "decreases", "decreased", "downregulat", "lower",
                   "reduced", "reduce", "loss", "inhibit", "suppress", "drop", "fall")


@dataclass
class HypothesisResult:
    gene: str
    present: bool                       # was the gene measured in this dataset
    log2fc: Optional[float]
    p_value: Optional[float]
    observed_direction: Optional[str]   # 'up' | 'down' | None
    claimed_direction: Optional[str]    # direction the question asserted
    significant: Optional[bool]
    supports_claim: Optional[bool]      # observed == claimed AND significant
    note: str = ""

    def as_dict(self) -> dict:
        return {k: (v if not isinstance(v, float) or not math.isnan(v) else None)
                for k, v in self.__dict__.items()}


def claimed_direction(question: str) -> Optional[str]:
    """The direction the question ASSERTS, for contrarian/gene-naming questions.

    Heuristic: the last direction word in the question is the claim. This handles
    the contrarian form "Whereas X typically *increases*, does it paradoxically
    *decrease*?" -> claim = 'down'. Questions with only a *relative* assertion
    ("opposite direction", "reversed") and no explicit up/down word return None
    (inconclusive without a textbook baseline).
    """
    q = (question or "").lower()
    last_dir = None
    last_pos = -1
    for word in _DIRECTION_UP:
        i = q.find(word)
        if i > last_pos:
            last_pos, last_dir = i, "up"
    for word in _DIRECTION_DOWN:
        i = q.find(word)
        if i > last_pos:
            last_pos, last_dir = i, "down"
    return last_dir


def _gene_column(genes: Sequence, named: str) -> Optional[int]:
    named = named.upper()
    for i, g in enumerate(genes or []):
        if str(g).upper() == named:
            return i
    return None


def evaluate_gene_hypothesis(expr, genes, labels, named_gene: str,
                             claimed_dir: Optional[str] = None) -> HypothesisResult:
    """Test whether ``named_gene`` moves in ``claimed_dir`` between the two groups.

    ``expr`` is a samples x genes matrix (numpy array or list-of-lists);
    ``genes`` the column symbols; ``labels`` the per-sample binary group labels.
    Reuses a plain two-sample t-test (consistent with the DE analyzer).
    """
    named = (named_gene or "").upper()
    col = _gene_column(genes, named)
    if col is None or expr is None or labels is None:
        return HypothesisResult(gene=named_gene, present=False, log2fc=None,
                                p_value=None, observed_direction=None,
                                claimed_direction=claimed_dir, significant=None,
                                supports_claim=None,
                                note="gene not measured in this dataset")
    try:
        arr = np.asarray(expr, dtype=float)
        if arr.ndim != 2 or arr.shape[1] <= col:
            return HypothesisResult(gene=named_gene, present=False, log2fc=None,
                                    p_value=None, observed_direction=None,
                                    claimed_direction=claimed_dir, significant=None,
                                    supports_claim=None, note="expression shape mismatch")
        vals = arr[:, col]
    except Exception as e:  # noqa: BLE001
        return HypothesisResult(gene=named_gene, present=False, log2fc=None,
                                p_value=None, observed_direction=None,
                                claimed_direction=claimed_dir, significant=None,
                                supports_claim=None, note=f"expr read error: {e}")

    groups = {}
    for v, lab in zip(vals, labels):
        groups.setdefault(lab, []).append(float(v))
    if len(groups) < 2:
        return HypothesisResult(gene=named_gene, present=True, log2fc=None,
                                p_value=None, observed_direction=None,
                                claimed_direction=claimed_dir, significant=None,
                                supports_claim=None, note="not a binary design")
    keys = sorted(groups.keys(), key=lambda k: str(k))
    a = np.array([x for x in groups[keys[0]] if not math.isnan(x)])
    b = np.array([x for x in groups[keys[1]] if not math.isnan(x)])
    if len(a) < 2 or len(b) < 2:
        return HypothesisResult(gene=named_gene, present=True, log2fc=None,
                                p_value=None, observed_direction=None,
                                claimed_direction=claimed_dir, significant=None,
                                supports_claim=None, note="group too small")
    try:
        from scipy.stats import ttest_ind
        t, p = ttest_ind(a, b, nan_policy="omit")
        if p is None or (isinstance(p, float) and math.isnan(p)):
            p = 1.0
    except Exception as e:  # noqa: BLE001
        return HypothesisResult(gene=named_gene, present=True, log2fc=None,
                                p_value=None, observed_direction=None,
                                claimed_direction=claimed_dir, significant=None,
                                supports_claim=None, note=f"t-test failed: {e}")

    mean_a, mean_b = float(np.nanmean(a)), float(np.nanmean(b))
    log2fc = math.log2((mean_b + 1e-6) / (mean_a + 1e-6))  # group[1] vs group[0]
    observed = "up" if log2fc > 0 else "down"
    significant = bool(p < 0.05)
    if claimed_dir is None:
        supports = None  # relative claim ("opposite"/"reversed") -> no baseline to judge
    else:
        supports = bool(observed == claimed_dir and significant)
    note = ("contrarian claim SUPPORTED" if supports
            else ("contrarian claim NOT supported (textbook held or not significant)"
                  if claimed_dir is not None else "relative claim; no baseline to test against"))
    return HypothesisResult(
        gene=named_gene, present=True, log2fc=round(log2fc, 4),
        p_value=round(float(p), 6), observed_direction=observed,
        claimed_direction=claimed_dir, significant=significant,
        supports_claim=supports, note=note)


def evaluate_question_hypothesis(question: str, expr, genes, labels) -> Optional[HypothesisResult]:
    """Convenience: extract the named gene + claimed direction from a question and test it.

    Returns None if the question names no specific gene (exploratory) — the
    gene-specific primitive only applies to gene-naming questions.
    """
    from biodisc_core.fixed_pipeline.value_of_compute import extract_named_genes
    named = extract_named_genes(question)
    if not named:
        return None
    claim = claimed_direction(question)
    # if multiple genes named, test the first (the question's subject)
    return evaluate_gene_hypothesis(expr, genes, labels, named[0], claimed_dir=claim)
