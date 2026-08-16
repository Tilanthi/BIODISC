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
"""Literature-claim Contradiction Detector (rebuild item 3).

Evidence: every paradigm overturn involved a textbook claim contradicted by
direct evidence — "the stomach is sterile" (H. pylori), "adult brain cannot
generate new neurons" (adult neurogenesis), "infectious agents require nucleic
acid" (prions), "genes are contiguous" (splicing). The pattern: an explicit,
testable claim in the literature + data that contradicts it.

This detector MINES the literature for explicit, testable claims ("X does not
occur", "Y requires Z") and forms contradiction candidates: "Challenge this
claim — is there data that contradicts it?" The evidence-grounded version of
"contrarian": instead of guessing a contrarian direction, it IDENTIFIES a
specific published claim and asks whether the data agrees.

First version (V9.0): a curated set of historical overturnable claims (the
validation set — the detector should find this pattern) + a regex claim-extractor
for mining new claims from PubMed abstracts. The data-contradiction check (actually
finding contradicting data in datasets) is the next step — for now, the detector
identifies the TARGET (the claim worth challenging) and forms the testable hypothesis.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

from .candidate import DiscoveryCandidate

logger = logging.getLogger(__name__)

# Historical textbook claims that were overturned — the validation set. The
# detector should recognize this PATTERN (explicit, mechanistic, testable claim)
# in new literature.
HISTORICAL_CLAIMS = [
    {"claim": "the stomach is sterile", "field": "gastroenterology",
     "overturned_by": "Helicobacter pylori (1982)",
     "test": "culture bacteria from gastric biopsy"},
    {"claim": "adult brain cannot generate new neurons", "field": "neuroscience",
     "overturned_by": "adult neurogenesis (1998)",
     "test": "BrdU/tritiated-thymidine labeling in adult hippocampus"},
    {"claim": "all infectious agents require nucleic acid", "field": "microbiology",
     "overturned_by": "prions (1982)",
     "test": "infectivity survives nuclease + UV treatment"},
    {"claim": "genes are contiguous DNA sequences", "field": "genetics",
     "overturned_by": "mRNA splicing (1977)",
     "test": "compare mRNA length to encoding DNA (electron microscopy)"},
    {"claim": "RNA is only informational (cannot catalyze reactions)", "field": "molecular_biology",
     "overturned_by": "ribozymes (1982)",
     "test": "test RNA for catalytic activity without protein"},
    {"claim": "cell fate is irreversibly determined after differentiation", "field": "cell_biology",
     "overturned_by": "cellular reprogramming / Yamanaka factors (2006)",
     "test": "force expression of reprogramming factors in differentiated cells"},
    {"claim": "species boundaries are fixed", "field": "evolution",
     "overturned_by": "horizontal gene transfer (1960s+)",
     "test": "phylogenetic discordance across genes"},
]

# Regex patterns for extracting explicit, testable claims from text.
# These capture the "mechanistic assertion" structure that's overturnable.
CLAIM_PATTERNS = [
    r"(?:never|does not|cannot|impossible|no evidence)\b[^.]{5,80}",
    r"(?:always|only|exclusively|requires?|must)\b[^.]{5,80}",
    r"(?:is sterile|is fixed|is irreversible|is impossible)\b[^.]{0,60}",
]


def extract_claims(text: str, max_claims: int = 10) -> List[str]:
    """Extract explicit, testable claims from text (PubMed abstracts, papers).

    Looks for mechanistic assertions ("X never happens", "Y requires Z") that are
    the kind of claim paradigm-overturns target. Returns the matched claim strings.
    """
    if not text:
        return []
    # split into sentences (rough)
    sentences = re.split(r'[.!?]\s+', text)
    claims = []
    for sent in sentences:
        for pattern in CLAIM_PATTERNS:
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                claim = sent.strip()[:120]
                if claim not in claims:
                    claims.append(claim)
                break
    return claims[:max_claims]


def detect_contradictions(text_corpus: Optional[str] = None,
                          literature_gate=None,
                          include_historical: bool = True) -> List[DiscoveryCandidate]:
    """Form contradiction candidates from explicit literature claims.

    Args:
        text_corpus: optional text (abstract(s)) to mine for NEW claims.
        literature_gate: for novelty scoring (None = neutral 0.5).
        include_historical: include the curated historical-claims validation set.
    """
    candidates: List[DiscoveryCandidate] = []

    # Historical validation set (known overturnable-claim patterns)
    if include_historical:
        for hc in HISTORICAL_CLAIMS:
            novelty = _novelty(hc["claim"], literature_gate)
            candidates.append(DiscoveryCandidate(
                kind="literature_contradiction",
                claim=f"Challenge: '{hc['claim']}' — test whether {hc['test']}",
                evidence={"original_claim": hc["claim"], "field": hc["field"],
                          "historical_overturn": hc["overturned_by"],
                          "contradiction_test": hc["test"]},
                methods=["contradiction"],
                novelty=novelty, importance=0.8, surprise=0.9,
                testable_with_existing_data=True,
            ))

    # Mine new claims from text corpus
    if text_corpus:
        extracted = extract_claims(text_corpus)
        for claim_text in extracted:
            novelty = _novelty(claim_text, literature_gate)
            candidates.append(DiscoveryCandidate(
                kind="literature_contradiction",
                claim=f"Challenge: '{claim_text}' — is there data that contradicts this?",
                evidence={"extracted_claim": claim_text, "source": "text_corpus"},
                methods=["contradiction"],
                novelty=novelty, importance=0.5, surprise=0.7,
                testable_with_existing_data=True,
            ))

    logger.info("contradiction detector: %d candidates", len(candidates))
    return candidates


def _novelty(claim: str, literature_gate) -> float:
    if literature_gate is None:
        return 0.5
    try:
        verdict = literature_gate.assess(claim)
        if getattr(verdict, "status", "") == "retrieval_failed":
            return 0.5
        sim = getattr(verdict, "max_similarity", 0.0) or 0.0
        return max(0.0, min(1.0, 1.0 - sim))
    except Exception:  # noqa: BLE001
        return 0.5
