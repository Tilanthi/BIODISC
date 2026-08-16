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
"""LLM-driven specific-question generator (AlphaEvolve-style co-evolved targets).

Phase 2 (P2.3): replaces the static 18-question list in specific_questions.py as
the SOURCE of discovery questions. An LLM proposes specific, mechanistic,
testable biological questions; a generic/template GATE filters out broad or
saturated-field phrasings (the same peer-review concern specific_questions.py
was built to address, now applied to LLM output). The active discovery loop can
adopt this via get_questions_via_llm(); specific_questions.py remains a fallback.
"""
import logging
import re
from dataclasses import dataclass
from typing import Callable, List

logger = logging.getLogger(__name__)

Proposer = Callable[[str, str], str]  # (system, user) -> raw model text

# Heuristic markers of broad / saturated-field / template questions.
_GENERIC_PHRASES = {
    "in general", "overall", "broadly", "various genes", "many genes",
    "gene expression in general", "important genes", "key genes",
    "patient stratification", "overall survival", "general mechanism",
}
# A specific anchor: an uppercase gene/protein-like token (BRCA1, STAT3, IL-6, PARP, AMPK).
_GENE_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)?\b")
# Specific disease / condition / intervention terms also count as anchors.
_SPECIFIC_TERMS = re.compile(
    r"\b(inhibitor|mutation|knockdown|overexpression|phosphorylation|carcinoma|"
    r"adenocarcinoma|glioblastoma|knockout|deletion|amplification|therapy|"
    r"treated|untreated)\b",
    re.I,
)


def is_generic_question(question: str) -> bool:
    """True if a question is too generic/template-like to be a novel target."""
    q = (question or "").strip()
    if len(q) < 25:
        return True
    ql = q.lower()
    if sum(1 for p in _GENERIC_PHRASES if p in ql) >= 2:
        return True
    has_anchor = bool(_GENE_TOKEN.search(q) or _SPECIFIC_TERMS.search(q))
    return not has_anchor


def parse_questions(raw: str) -> List[str]:
    """Extract question strings from raw model output (one per line, numbered or bulleted)."""
    out = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line:
            continue
        # strip leading numbering / bullets / quotes.
        line = re.sub(r"^\s*(\d+[\.\)]|-|\*|•)\s*", "", line)
        line = line.strip("`\"' ")
        if line.endswith("?") or len(line) > 25:  # keep plausible questions
            out.append(line)
    return out


_QUESTION_SYSTEM = (
    "You propose specific, novel, testable biological research questions for a "
    "discovery system that answers them with REAL gene-expression data. Each "
    "question MUST name a specific gene/protein/pathway AND a specific condition "
    "or intervention (e.g. 'Does STAT3 activation differ between IL-6 treated and "
    "untreated glioblastoma cells?'). Do NOT propose broad or saturated-field "
    "questions like 'What genes are important in cancer?'. Output ONE question per line."
)


def _build_question_prompt(n: int) -> str:
    return (f"Propose {n} specific, mechanistic, novel biological questions. "
            f"One per line. No numbering, no commentary.")


@dataclass
class GeneratedQuestion:
    text: str
    rejected: bool
    reason: str = ""


class QuestionGenerator:
    """Generates biological questions via an LLM and gates out generic ones."""

    def __init__(self, proposer: Proposer, n_per_call: int = 10):
        self.proposer = proposer
        self.n_per_call = n_per_call

    def generate(self, n: int = None) -> List[GeneratedQuestion]:
        n = n or self.n_per_call
        raw = self.proposer(_QUESTION_SYSTEM, _build_question_prompt(n))
        results = []
        for q in parse_questions(raw):
            if is_generic_question(q):
                results.append(GeneratedQuestion(q, rejected=True, reason="generic/template"))
            else:
                results.append(GeneratedQuestion(q, rejected=False))
        return results


def get_questions_via_llm(proposer: Proposer, n: int = 10) -> List[str]:
    """Return only the non-generic questions from one LLM call (drop rejects)."""
    gen = QuestionGenerator(proposer, n_per_call=n)
    return [g.text for g in gen.generate(n) if not g.rejected]
