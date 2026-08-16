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
"""Dataset re-mining framework (rebuild item 2).

The evidence: scRNA-seq tumor data revealed novel cell states, TCGA enabled
molecular cancer taxonomy, AlphaFold enabled drug-target discovery — these were
"second-wave" reanalyses of existing public data with novel questions, and they
are HIGHLY automatable (BIODISC's core strength).

This module identifies high-value public datasets from measurement revolutions
and proposes novel re-mining questions the original authors didn't pursue.
Each dataset type needs its own data connector (downloader + parser); this
framework defines the interface + curated targets. The connectors are the
data-engineering follow-up.

FIRST VERSION (V9.0): the framework + curated re-mining targets from the
breakthrough analysis. Produces DiscoveryCandidates for each target (logged for
human review). When connectors are built, this module will actually download +
analyze the data.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .candidate import DiscoveryCandidate

logger = logging.getLogger(__name__)


@dataclass
class ReminingTarget:
    """A dataset + a novel question to re-mine it with."""
    source: str               # 'TCGA' | 'scRNA-seq' | 'AlphaFold' | 'GEO'
    dataset_id: str
    original_analysis: str    # what the authors did
    novel_question: str       # what to ask instead
    connector: str = ""       # which connector will handle the download/parse
    priority: float = 0.0     # 0-1, higher = more promising
    rationale: str = ""


# Curated re-mining opportunities (from the breakthrough analysis evidence).
# Each is a dataset that EXISTS publicly, where a NOVEL question (not the
# original analysis) could yield a breakthrough.
REMINING_OPPORTUNITIES: List[ReminingTarget] = [
    ReminingTarget(
        source="TCGA", dataset_id="pan-cancer-atlas",
        original_analysis="differential expression by tumor type (one-at-a-time)",
        novel_question="cross-cancer convergence: which gene modules are SHARED across "
                       "tumor types, and which are tissue-specific?",
        connector="tcga_bulk_rnaseq",
        priority=0.9,
        rationale="TCA's 33 tumor types have been analyzed individually but rarely "
                  "cross-compared at the module level. Pan-cancer shared modules could "
                  "reveal universal cancer vulnerabilities — exactly the 'second-wave' "
                  "reanalysis that yielded breakthroughs."),
    ReminingTarget(
        source="scRNA-seq", dataset_id="tumor-microenvironment-atlases",
        original_analysis="clustering + cell-type annotation",
        novel_question="trajectory inference: which cell states are TRANSITIONAL "
                       "(stem-like, plastic) vs stable? Which transitions correlate "
                       "with treatment resistance?",
        connector="scrna_scanpy",
        priority=0.8,
        rationale="Most scRNA-seq tumor papers do clustering but SKIP trajectory "
                  "inference. Cell-state plasticity is a frontier in cancer biology "
                  "(EMT, drug tolerance) and the data exists."),
    ReminingTarget(
        source="AlphaFold", dataset_id="human-proteome-structures",
        original_analysis="per-protein structure prediction (one at a time)",
        novel_question="cross-protein: which DISORDERED regions (predicted by AlphaFold "
                       "low-confidence) are SHARED across protein families? Do they "
                       "represent a new class of regulatory elements?",
        connector="alphafold_ebi_api",
        priority=0.7,
        rationale="AlphaFold structures are mined per-protein for drug pockets, but "
                  "the CROSS-PROTEIN pattern of low-confidence (disordered) regions "
                  "hasn't been systematically analyzed. Intrinsically disordered "
                  "regions are a frontier in drug discovery."),
    ReminingTarget(
        source="GEO", dataset_id="under-studied-disease-bulk-rnaseq",
        original_analysis="DE between case and control (standard)",
        novel_question="cross-dataset synthesis: do the SAME gene modules respond "
                       "across different diseases/drugs/tissues? (the bridge pattern)",
        connector="geo_series_matrix (existing)",
        priority=0.6,
        rationale="BIODISC already downloads GEO. The novel question is not per-dataset "
                  "DE but CROSS-DATASET module comparison — the bridge pattern the "
                  "breakthrough analysis identified as highest-yield."),
]


def get_remining_targets() -> List[ReminingTarget]:
    """Return the curated re-mining opportunities."""
    return list(REMINING_OPPORTUNITIES)


def detect_remining_candidates() -> List[DiscoveryCandidate]:
    """Convert re-mining targets into DiscoveryCandidates for the convergence pool.

    First version: logs the targets as candidates (for human review). When
    connectors are built, this module will download + analyze each dataset and
    produce DATA-DRIVEN candidates (not just the target description).
    """
    candidates = []
    for t in REMINING_OPPORTUNITIES:
        candidates.append(DiscoveryCandidate(
            kind="remining_finding",
            claim=f"Re-mine {t.source} ({t.dataset_id}) with novel question: {t.novel_question}",
            evidence={
                "source": t.source,
                "dataset_id": t.dataset_id,
                "original_analysis": t.original_analysis,
                "novel_question": t.novel_question,
                "connector": t.connector,
                "rationale": t.rationale,
            },
            methods=["remining"],
            novelty=0.6,   # novel question by construction
            importance=t.priority,
            surprise=0.5,
            testable_with_existing_data=(t.connector == "geo_series_matrix (existing)"),
        ))
    logger.info("re-mining framework: %d targets", len(candidates))
    return candidates
