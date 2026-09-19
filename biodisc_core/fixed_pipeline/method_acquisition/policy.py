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
"""RSI confinement policy (V9.1): plumbing vs scientific algorithm.

Paper2Agent's rule — "Do not invent scientific algorithms to fill repository
gaps" — applied to BIODISC's self-improvement loop. The RSI miner remains
excellent at PLUMBING (ontology maps, IO bounds, reliability, orchestration)
but must not invent scientific algorithms: changes to statistical methods,
scoring formulas, and gates' scientific behavior route to the method-acquisition
queue (admission.py) instead of RSI-direct application.

The default for anything unclassified is CONSERVATIVE (scientific_algorithm ->
acquisition route): an unknown change is never silently auto-applied to the
scientific core.
"""
from __future__ import annotations

from typing import Optional

# Substrings identifying the pipeline's SCIENTIFIC core (algorithms that turn
# data into claims). Editing these changes what counts as a discovery.
SCIENTIFIC_PATH_PATTERNS = (
    "differential_expression",
    "anomaly_miner",
    "gene_specific_hypothesis",
    "fdr_significance_gate",
    "replication_gate",
    "literature_gate",
    "value_of_compute",      # the EV scoring formula and its vocabularies
    "pathway_analysis",
    "benchmark",             # truth fixtures define what 'correct' means
    "cross_dataset_synthesis",
)

PLUMBING = "plumbing"
SCIENTIFIC = "scientific_algorithm"

# Explicit per-theme classification for every rsi_miner THEME_TAXONOMY entry.
# plumbing = data maps, IO, reliability, orchestration.
# scientific = the fix would alter statistical methods or claim-shaping.
THEME_CLASS = {
    "significance_failed": SCIENTIFIC,     # DE parameters / thresholds
    "duplicate_profile": PLUMBING,         # question/dataset diversity plumbing
    "organism_mismatch": PLUMBING,         # organism normalization map
    "tissue_mismatch": PLUMBING,           # tissue ontology map
    "disease_mismatch": PLUMBING,          # disease ontology map
    "dataset_question_mismatch": PLUMBING, # question<->dataset pinning
    "literature_known": PLUMBING,          # question reframing policy
    "probe_gene_failed": PLUMBING,         # GPL probe->gene mapping coverage
    "no_datasets": PLUMBING,               # dataset pool
    "generation_failed": PLUMBING,         # reliability
    "exception": PLUMBING,                 # reliability
    "abandoned_mid_validation": PLUMBING,  # watchdog/reliability
    "template_question": SCIENTIFIC,       # question templates shape claims
}


def classify_path(path: str) -> str:
    """Classify a file path (repo-relative) as scientific core or plumbing."""
    p = str(path)
    return SCIENTIFIC if any(pat in p for pat in SCIENTIFIC_PATH_PATTERNS) else PLUMBING


def classify_proposal(theme: str) -> dict:
    """Route an RSI proposal: scientific algorithms go to acquisition, not RSI-direct.

    Unknown themes default to the conservative scientific route.
    """
    change_class = THEME_CLASS.get(theme, SCIENTIFIC)  # conservative default
    route = "method_acquisition" if change_class == SCIENTIFIC else "rsi_direct"
    return {"change_class": change_class, "route": route}


def route_note(change_class: Optional[str]) -> str:
    """One-line explanation for the proposals doc."""
    if change_class == SCIENTIFIC:
        return ("scientific algorithm — must pass method-acquisition admission "
                "(reference agreement + store FPR check + human review), never "
                "RSI-direct")
    return "plumbing — eligible for RSI-direct application (still human-gated)"


__all__ = ["classify_path", "classify_proposal", "route_note",
           "SCIENTIFIC_PATH_PATTERNS", "THEME_CLASS", "PLUMBING", "SCIENTIFIC"]
