"""Breakthrough discovery package — the multi-modality rebuild.

The old pipeline was single-modality (one question -> one dataset -> DE). This
package implements the evidence-based rebuild: multiple independent discovery
*modalities* (cross-domain bridges, literature-claim contradictions, anomalies-in-
context, dataset re-mining) each emit ``DiscoveryCandidate`` objects into a shared
``CandidatePool``; a ``ConvergenceScorer`` (item 5) flags candidates that >=3
independent methods agree on as high-potential; the survivors flow through the
existing 6-layer validation + replication anchor (item 6) as the final gate.

Grounded in the multi-agent analysis of how real biology breakthroughs happen:
the highest-yield, automatable mechanisms are cross-domain synthesis, second-wave
data re-mining, and literature-vs-data contradiction — not single-contrast DE on
exhausted datasets.
"""
from .candidate import DiscoveryCandidate, CandidatePool
from .convergence import ConvergenceScorer

__all__ = ["DiscoveryCandidate", "CandidatePool", "ConvergenceScorer"]
