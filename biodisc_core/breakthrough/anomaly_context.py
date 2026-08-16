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
"""Anomaly-in-context adapter (rebuild item 4).

Wraps the existing anomaly_miner (V8.0.38-40) into the DiscoveryCandidate model.
The anomaly miner finds observed surprises (direction-flips-vs-prior, extreme
effects); this adapter converts those into candidates the convergence scorer can
merge with candidates from other methods (bridge, contradiction).

"Mechanistic expectation" is approximated data-driven: the gene's prior direction
in the genuine store = the expectation; a flip = a mechanistic violation.
Persistence across datasets = prior_in_n_datasets (a gene that flips in multiple
contexts is a stronger signal than a one-off). A real literature-based
"textbook-direction" baseline is the next-gen enhancement (anomaly_vs_expectation).
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .candidate import DiscoveryCandidate

logger = logging.getLogger(__name__)


def detect_anomaly_candidates(de_results=None, prior_directions=None,
                              dataset_id: str = "", gene_results=None,
                              top_k: int = 10) -> List[DiscoveryCandidate]:
    """Run the anomaly miner and convert results to DiscoveryCandidates."""
    from biodisc_core.fixed_pipeline.anomaly_miner import mine_anomalies
    anomalies = mine_anomalies(de_results, prior_directions, dataset_id,
                               top_k=top_k, gene_results=gene_results)
    candidates = []
    for a in anomalies:
        candidates.append(DiscoveryCandidate(
            kind="anomaly_in_context",
            claim=a.claim,
            gene=a.gene,
            evidence={
                "anomaly_kind": a.kind,
                "observed_direction": a.observed_direction,
                "prior_direction": a.prior_direction,
                "log2fc": a.log2fc,
                "p_value": a.p_value,
                "prior_in_n_datasets": a.prior_in_n_datasets,
                "anomaly_score": a.score,
            },
            methods=["anomaly"],
            novelty=0.5,  # neutral until Gate-2 checks the specific claim
            importance=a.importance,
            surprise=a.surprise,
            consensus_conflict="direction_flip" in a.kind,  # R2: flip = consensus conflict
            source_datasets=[dataset_id] if dataset_id else [],
            testable_with_existing_data=True,
        ))
    logger.info("anomaly-in-context: %d candidates from %s", len(candidates), dataset_id or "(no dataset)")
    return candidates
