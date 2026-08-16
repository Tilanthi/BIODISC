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
"""Gate-2 — REAL literature-novelty check via PubMed.

Replaces the keyword-heuristic ``novelty_estimator`` (which itself commented
"A real novelty check should be literature-similarity based, not a keyword
blacklist"). A claim is checked against retrieved PubMed abstracts:

* build a query from the claim (gene symbols + condition terms),
* esearch PMIDs, efetch abstracts,
* compute a TF-cosine similarity (gene symbols + content terms, stopword-filtered)
  between the claim and each retrieved abstract,
* verdict:
    - ``novel``           max similarity < threshold  -> claim NOT entailed
    - ``known``           max similarity >= threshold -> claim already in literature
                          (textbook / already-established) -> reject (Gate-2)
    - ``retrieval_failed`` network/query error         -> NON-blocking, NOT cached

Robustness (ASTRA §7.4): transient ``retrieval_failed`` verdicts are NEVER
cached, so a later run re-checks instead of inheriting a permanent failure.
Only ``novel``/``known`` verdicts are memoised. A ``retrieval_failed`` verdict
is non-blocking for the pipeline (PubMed may be unreachable in the sandbox) —
the discovery proceeds as a *candidate*, never as genuine.

This is deliberately dependency-light: TF-cosine over fetched abstracts, no
external embedding API (which would need network in the sandbox).
"""
import hashlib
import logging
import math
import re
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Terms that add noise to a PubMed query / similarity vector.
_STOPWORDS = {
    "the", "a", "an", "of", "in", "to", "and", "or", "for", "with", "by", "on",
    "is", "are", "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "it", "its", "as", "at", "from", "which", "how", "does", "do",
    "what", "between", "than", "then", "such", "may", "can", "has", "have",
    "had", "not", "but", "their", "they", "we", "our", "his", "her", "gene",
    "genes", "expression", "cells", "cell", "study", "results", "showed",
    "found", "increased", "decreased", "compared", "normal", "human", "using",
}


@dataclass
class LiteratureVerdict:
    status: str  # novel | known | retrieval_failed
    max_similarity: float
    n_papers_checked: int
    evidence_pmids: List[str] = field(default_factory=list)
    query: str = ""
    reason: str = ""


def _is_gene_symbol(tok: str) -> bool:
    """Heuristic: ALL-CAPS alphabetic token, length 2-7, possibly with digits (e.g. TP53, BCL2)."""
    if 2 <= len(tok) <= 7 and tok[:1].isalpha():
        return tok.isupper() or re.fullmatch(r"[A-Z][A-Z0-9]{1,6}", tok) is not None
    return False


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9]{1,}", text.lower())


def _content_tokens(text: str) -> List[str]:
    return [t for t in _tokenize(text) if t not in _STOPWORDS and len(t) > 2]


def _gene_symbols(text: str) -> List[str]:
    raw = re.findall(r"\b[A-Z][A-Z0-9]{1,6}\b", text)
    return [t for t in raw if t.lower() not in _STOPWORDS]


def _weighted_vector(text: str) -> dict:
    """Term vector: gene symbols weighted 3x (strong entailment signal), content terms 1x."""
    vec = {}
    for g in set(_gene_symbols(text)):
        vec[g.lower()] = vec.get(g.lower(), 0.0) + 3.0
    for t in _content_tokens(text):
        vec[t] = vec.get(t, 0.0) + 1.0
    return vec


def _cosine(va: dict, vb: dict) -> float:
    if not va or not vb:
        return 0.0
    dot = sum(va[t] * vb.get(t, 0.0) for t in va)
    na = math.sqrt(sum(v * v for v in va.values()))
    nb = math.sqrt(sum(v * v for v in vb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _build_query(text: str, max_terms: int = 6) -> str:
    """PubMed query: prefer gene symbols + top content terms."""
    genes = list(dict.fromkeys(_gene_symbols(text)))  # de-dup, preserve order
    content = list(dict.fromkeys(_content_tokens(text)))
    terms = (genes + content)[:max_terms]
    return " AND ".join(terms) if terms else text[:80]


class LiteratureNoveltyGate:
    """Real PubMed literature-novelty gate."""

    def __init__(
        self,
        similarity_threshold: float = 0.55,
        max_results: int = 8,
        timeout: float = 15.0,
        enabled: bool = True,
    ):
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        self.timeout = timeout
        self.enabled = enabled
        self._cache = {}  # claim_hash -> LiteratureVerdict (novel/known only)
        self.assessments = 0

    # -- network layer -------------------------------------------------------
    def _search_pmids(self, query: str) -> List[str]:
        params = {"db": "pubmed", "term": query, "retmax": self.max_results, "retmode": "json"}
        resp = requests.get(ESEARCH_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get("esearchresult", {}).get("idlist", []) or []

    def _fetch_abstracts(self, pmids: List[str]) -> List[Tuple[str, str]]:
        if not pmids:
            return []
        time.sleep(0.4)  # NCBI rate limit courtesy
        params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "abstract", "retmode": "xml"}
        resp = requests.get(EFETCH_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        out = []
        for art in root.findall(".//PubmedArticle"):
            pmid_el = art.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else ""
            parts = [t.text or "" for t in art.findall(".//AbstractText")]
            abstract = " ".join(parts).strip()
            title_el = art.find(".//ArticleTitle")
            title = title_el.text if title_el is not None else ""
            if abstract or title:
                out.append((pmid, f"{title} {abstract}"))
        return out

    def _default_fetch(self, query: str) -> List[Tuple[str, str]]:
        pmids = self._search_pmids(query)
        return self._fetch_abstracts(pmids)

    # -- public API ----------------------------------------------------------
    def assess(
        self,
        claim_text: str,
        question: Optional[str] = None,
        fetcher: Optional[Callable[[str], List[Tuple[str, str]]]] = None,
    ) -> LiteratureVerdict:
        """Assess whether ``claim_text`` is entailed by PubMed literature."""
        if not self.enabled:
            return LiteratureVerdict("novel", 0.0, 0, [], "", "literature gate disabled")
        self.assessments += 1
        text = f"{claim_text} {question or ''}".strip()
        key = hashlib.md5(text.lower().encode("utf-8")).hexdigest()
        if key in self._cache:
            return self._cache[key]

        query = _build_query(text)
        try:
            docs = (fetcher or self._default_fetch)(query)
        except Exception as e:  # noqa: BLE001 - network must not crash the pipeline
            logger.warning("Gate-2 retrieval failed (NOT cached): %s", e)
            return LiteratureVerdict("retrieval_failed", 0.0, 0, [], query, f"retrieval error: {e}")

        if not docs:
            verdict = LiteratureVerdict(
                "novel", 0.0, 0, [], query,
                "no prior literature retrieved for query (low-confidence novel)",
            )
            self._cache[key] = verdict
            return verdict

        claim_vec = _weighted_vector(text)
        best_sim = 0.0
        best_pmids = []
        for pmid, abstract in docs:
            sim = _cosine(claim_vec, _weighted_vector(abstract))
            if sim > best_sim:
                best_sim = sim
            if sim >= self.similarity_threshold:
                best_pmids.append(pmid)

        if best_sim >= self.similarity_threshold:
            verdict = LiteratureVerdict(
                "known", best_sim, len(docs), best_pmids[:5], query,
                f"claim entailed by literature (max similarity {best_sim:.2f})",
            )
        else:
            verdict = LiteratureVerdict(
                "novel", best_sim, len(docs), [], query,
                f"claim not entailed by literature (max similarity {best_sim:.2f})",
            )
        self._cache[key] = verdict  # cache only terminal novel/known verdicts
        return verdict


def create_literature_novelty_gate(**kwargs) -> LiteratureNoveltyGate:
    return LiteratureNoveltyGate(**kwargs)


__all__ = [
    "LiteratureNoveltyGate", "LiteratureVerdict", "create_literature_novelty_gate",
]
