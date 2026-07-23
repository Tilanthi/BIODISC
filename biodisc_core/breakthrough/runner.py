"""Breakthrough discovery runner — invokes all modalities, converges, ranks.

This is the integration point (items 1+3+4+5). It runs every discovery modality,
collects their candidates into a shared pool, and the ConvergenceScorer flags
candidates that >= N independent methods agree on as high-potential. The survivors
then flow through the existing 6-layer validation + replication anchor (item 6)
as the final gate.

Item 2 (dataset re-mining) plugs in here once its data connectors are built — the
runner has a slot for it. For now it runs bridge + contradiction + anomaly.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .candidate import CandidatePool, DiscoveryCandidate
from .convergence import ConvergenceScorer
from .bridge_engine import detect_bridges
from .contradiction_detector import detect_contradictions
from .anomaly_context import detect_anomaly_candidates

logger = logging.getLogger(__name__)


def run_breakthrough_discovery(
    literature_gate=None,
    de_results: Optional[Dict] = None,
    prior_directions: Optional[Dict] = None,
    dataset_id: str = "",
    gene_results: Optional[List] = None,
    text_corpus: Optional[str] = None,
    min_convergence: int = 3,
) -> Dict[str, Any]:
    """Run all discovery modalities, converge, and return ranked candidates.

    Returns:
        {"pool_size": N, "high_potential": [...], "all_ranked": [...]}
    """
    pool = CandidatePool()

    # Item 1: cross-domain bridge engine
    pool.add_all(detect_bridges(literature_gate))

    # Item 3: literature-claim contradiction detector
    pool.add_all(detect_contradictions(text_corpus, literature_gate))

    # Item 4: anomaly-in-context (from a DE result if available)
    if de_results or gene_results:
        pool.add_all(detect_anomaly_candidates(
            de_results, prior_directions, dataset_id, gene_results))

    # Item 2: dataset re-mining (slot — connector not yet built)
    # pool.add_all(detect_remining_candidates(...))

    # Item 5: convergence scoring
    scorer = ConvergenceScorer(min_methods=min_convergence)
    ranked = scorer.score_pool(pool)

    high = [c for c in ranked if c.high_potential]
    logger.info("breakthrough runner: %d candidates, %d high-potential (>= %d methods)",
                len(pool), len(high), min_convergence)

    return {
        "pool_size": len(pool),
        "high_potential": high,
        "all_ranked": ranked,
    }
