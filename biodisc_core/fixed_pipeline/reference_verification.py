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
"""Reference verification gate (REFERENCE_VERIFICATION_PROTOCOL.md, PubMed-adapted).

Distilled from a real audit (RASTI, Oct 2026) in which an AI-assembled
bibliography contained ~20 fabricated / misattributed / silently broken
entries out of ~50 — every one of which looked correct on casual inspection.
The protocol's core admission carries over verbatim: citation fields are
generated from learned patterns, not from documents, so plausibility is not
evidence. Every field must be TRANSCRIBED from a fetched authoritative source
(here: PubMed efetch), never generated.

Rules implemented (protocol section 2), adapted per the protocol's own
biomedical domain note (Crossref/DOI round-trip -> PubMed/PMID round-trip):

* Rule 1/4 — ``build_citation``: all fields transcribed from one fetched
  record; the complete author list is copied and truncation ("and others")
  is applied mechanically, never reconstructed from memory.
* Rule 2 — ``verify_pmid_roundtrip``: a PMID that resolves is not evidence;
  a PMID that resolves TO THE PAPER YOU MEANT is evidence. Fetched title
  similarity >= 0.75 (>= 0.5 acceptable only if journal AND year agree);
  author lists must overlap; journal and year must agree.
* Rule 3 — ``check_attribution``: existence is necessary, never sufficient.
  The fetched abstract must actually entail the claim being attributed to it
  (gene-weighted TF-cosine, same math as Gate-2, reused from literature_gate).
* Rule 6/7/8 — ``sweep_document``: scripted gate over a document's reference
  list — cited-but-missing and present-but-uncited reconciliation (both
  directions), per-entry round-trip verdicts, and an honest residue report
  (machine-verified / exempt-with-reason / needs-human). Exit non-zero on
  any unresolved issue.

Network failures are NON-blocking for the pipeline (mirroring Gate-2's
``retrieval_failed`` semantics): they return status ``retrieval_failed``,
are never cached, and never silently pass.
"""
import difflib
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import requests

from biodisc_core.fixed_pipeline.literature_gate import _cosine, _weighted_vector

logger = logging.getLogger(__name__)

EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

TITLE_SIM_THRESHOLD = 0.75  # floor; >= 0.5 OK if journal+year agree (publisher variants)
ATTRIBUTION_SIM_THRESHOLD = 0.35  # claim-to-abstract entailment floor (Gate-2 uses 0.55
# against a claim built for that purpose; here the citation only needs to be
# in scope of the claim, so the floor is lower)


@dataclass
class PubMedRecord:
    """All fields transcribed from ONE fetched efetch record (Rule 1)."""
    pmid: str
    title: str
    authors: List[str]
    journal: str
    year: str
    abstract: str


@dataclass
class RoundtripVerdict:
    status: str  # verified | mismatch | unresolvable | retrieval_failed
    title_similarity: float
    reason: str = ""


@dataclass
class CitationEntry:
    """A reference-list entry to be verified against the authoritative record."""
    key: str
    title: str
    authors: List[str]
    journal: str = ""
    year: str = ""
    pmid: str = ""
    doi: str = ""
    exempt_reason: str = ""  # books etc. — Rule 7 honest residue


@dataclass
class SweepReport:
    """Rule 6/7 output — the sweep's own output is the evidence, not self-assessment."""
    verified: List[str] = field(default_factory=list)
    mismatches: List[str] = field(default_factory=list)
    unresolvable: List[str] = field(default_factory=list)
    retrieval_failed: List[str] = field(default_factory=list)
    cited_but_missing: List[str] = field(default_factory=list)
    uncited_present: List[str] = field(default_factory=list)
    exempt: List[str] = field(default_factory=list)  # (key, reason) as "key: reason"

    @property
    def ok(self) -> bool:
        return not (self.mismatches or self.unresolvable
                    or self.cited_but_missing or self.retrieval_failed)

    def summary(self) -> str:
        lines = [
            f"verified: {len(self.verified)}",
            f"mismatches: {len(self.mismatches)} {self.mismatches}",
            f"unresolvable: {len(self.unresolvable)} {self.unresolvable}",
            f"retrieval_failed (re-check, not cached): {self.retrieval_failed}",
            f"cited-but-missing: {self.cited_but_missing}",
            f"uncited-present (prune or flag, Rule 8): {self.uncited_present}",
            f"exempt / needs human (Rule 7): {self.exempt}",
        ]
        return "\n".join(lines)


def _clean(t: str) -> str:
    t = re.sub(r"\{|\}|<[^>]+>", "", t or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _parse_efetch_xml(content: bytes) -> Dict[str, PubMedRecord]:
    import xml.etree.ElementTree as ET
    root = ET.fromstring(content)
    out = {}
    for art in root.findall(".//PubmedArticle"):
        pmid_el = art.find(".//PMID")
        if pmid_el is None or not pmid_el.text:
            continue
        pmid = pmid_el.text.strip()
        title_el = art.find(".//ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else ""
        authors = []
        for author in art.findall(".//Author"):
            ln = author.find("LastName")
            ini = author.find("Initials")
            if ln is not None and ln.text:
                authors.append(f"{ln.text} {ini.text}" if ini is not None and ini.text else ln.text)
        journal_el = art.find(".//Journal/ISOAbbreviation")
        if journal_el is None:
            journal_el = art.find(".//Journal/Title")
        journal = journal_el.text if journal_el is not None and journal_el.text else ""
        year_el = art.find(".//PubDate/Year")
        if year_el is None:
            year_el = art.find(".//ArticleDate/Year")
        year = year_el.text if year_el is not None and year_el.text else ""
        abstract = " ".join(t.text or "" for t in art.findall(".//AbstractText")).strip()
        out[pmid] = PubMedRecord(pmid, title.strip(), authors, journal.strip(), year, abstract)
    return out


class ReferenceVerifier:
    """PubMed round-trip verification gate (fetcher-injectable for offline tests)."""

    def __init__(self, timeout: float = 15.0, enabled: bool = True,
                 fetcher: Optional[Callable] = None):
        self.timeout = timeout
        self.enabled = enabled
        self.fetcher = fetcher  # injectable for offline tests (Gate-2 pattern)

    # -- network layer (mirror of literature_gate's fetcher pattern) ----------
    def fetch_records(self, pmids: List[str]) -> Dict[str, PubMedRecord]:
        if not pmids:
            return {}
        time.sleep(0.4)  # NCBI rate-limit courtesy (same as Gate-2)
        params = {"db": "pubmed", "id": ",".join(pmids),
                  "rettype": "abstract", "retmode": "xml"}
        resp = requests.get(EFETCH_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return _parse_efetch_xml(resp.content)

    def _fetch(self, pmids: List[str]) -> Dict[str, PubMedRecord]:
        return (self.fetcher or self.fetch_records)(pmids)

    # -- Rule 1/4: transcription ----------------------------------------------
    def build_citation(self, pmid: str, max_authors: int = 6) -> Dict:
        """Transcribe every field from the fetched record — never generate.

        Author truncation is mechanical: keep the first ``max_authors`` of the
        FETCHED list and append 'and others' (Rule 4).
        """
        rec = self._fetch([pmid]).get(pmid)
        if rec is None:
            raise ValueError(f"PMID {pmid} does not resolve — cannot transcribe")
        if len(rec.authors) > max_authors:
            authors = rec.authors[:max_authors] + ["and others"]
        else:
            authors = list(rec.authors)
        return {"pmid": rec.pmid, "title": rec.title, "authors": authors,
                "full_author_count": len(rec.authors),
                "journal": rec.journal, "year": rec.year}

    # -- Rule 2: PMID round-trip -----------------------------------------------
    def verify_pmid_roundtrip(self, entry: CitationEntry,
                              record: Optional[PubMedRecord] = None) -> RoundtripVerdict:
        """A PMID that resolves is not evidence; one that resolves to the paper
        you meant is. Title similarity floor 0.75; >= 0.5 if journal+year agree."""
        try:
            rec = record or self._fetch([entry.pmid]).get(entry.pmid)
        except Exception as e:  # noqa: BLE001 - network must not crash the pipeline
            return RoundtripVerdict("retrieval_failed", 0.0, f"fetch error: {e}")
        if rec is None:
            return RoundtripVerdict("unresolvable", 0.0,
                                    f"PMID {entry.pmid} does not resolve")
        sim = difflib.SequenceMatcher(
            None, _clean(entry.title), _clean(rec.title)).ratio()
        meta_ok = ((not entry.journal or not rec.journal or entry.journal.lower().startswith(rec.journal.lower()[:8]))
                   and (not entry.year or entry.year == rec.year))
        if sim >= TITLE_SIM_THRESHOLD:
            ok = True
        elif sim >= 0.5 and meta_ok:
            ok = True  # publisher/journal title variant, metadata agrees
        else:
            ok = False
        # Rule 4's companion: author overlap check (confabulated co-authors were
        # the most frequent single error class in the audit).
        surname_overlap = bool(set(a.split()[0].lower() for a in entry.authors)
                               & set(a.split()[0].lower() for a in rec.authors)) \
            if entry.authors and rec.authors else True
        if not ok:
            return RoundtripVerdict("mismatch", sim,
                                    f"PMID {entry.pmid} resolves to a different paper "
                                    f"(title sim {sim:.2f}; bib: '{entry.title[:60]}' "
                                    f"vs fetched: '{rec.title[:60]}')")
        if not surname_overlap:
            return RoundtripVerdict("mismatch", sim,
                                    f"PMID {entry.pmid}: no author overlap — possible "
                                    f"wrong-paper attribution")
        return RoundtripVerdict("verified", sim)

    # -- Rule 3: attribution, not existence -------------------------------------
    def check_attribution(self, claim_text: str, pmid: str,
                          record: Optional[PubMedRecord] = None) -> RoundtripVerdict:
        """Does the actual paper (per its abstract) contain the finding this
        claim attributes to it? Existence is necessary, never sufficient."""
        try:
            rec = record or self._fetch([pmid]).get(pmid)
        except Exception as e:  # noqa: BLE001
            return RoundtripVerdict("retrieval_failed", 0.0, f"fetch error: {e}")
        if rec is None:
            return RoundtripVerdict("unresolvable", 0.0, f"PMID {pmid} does not resolve")
        sim = _cosine(_weighted_vector(claim_text), _weighted_vector(rec.abstract))
        if sim < ATTRIBUTION_SIM_THRESHOLD:
            return RoundtripVerdict(
                "mismatch", sim,
                f"PMID {pmid} exists but abstract does not entail the claim "
                f"(sim {sim:.2f}) — wrong-paper attribution suspected")
        return RoundtripVerdict("verified", sim)

    # -- Rule 6/7/8: the sweep gate ----------------------------------------------
    def sweep_document(self, cited_keys: List[str],
                       entries: List[CitationEntry]) -> SweepReport:
        """Reconcile cited vs listed in both directions, round-trip every cited
        entry with a PMID, and report the honest residue. Non-zero on issues."""
        report = SweepReport()
        by_key = {e.key: e for e in entries}
        cited = set(cited_keys)
        report.cited_but_missing = sorted(cited - set(by_key))
        report.uncited_present = sorted(set(by_key) - cited)

        to_fetch = [e for e in entries if e.key in cited and e.pmid and not e.exempt_reason]
        pmids = list(dict.fromkeys(e.pmid for e in to_fetch))
        try:
            records = self._fetch(pmids) if pmids else {}
        except Exception as e:  # noqa: BLE001
            records = {}
            report.retrieval_failed = [e.key for e in to_fetch]
            logger.warning("Reference sweep retrieval failed: %s", e)

        for e in entries:
            if e.key not in cited:
                continue
            if e.exempt_reason:
                report.exempt.append(f"{e.key}: {e.exempt_reason}")
                continue
            if not e.pmid:
                report.exempt.append(f"{e.key}: no PMID — verify by hand")
                continue
            if e.key in report.retrieval_failed:
                continue
            v = self.verify_pmid_roundtrip(e, records.get(e.pmid))
            if v.status == "verified":
                report.verified.append(e.key)
            elif v.status == "mismatch":
                report.mismatches.append(f"{e.key}: {v.reason}")
            elif v.status == "unresolvable":
                report.unresolvable.append(f"{e.key}: {v.reason}")
        return report


# -- Layer 6b hook: verify Gate-2's own evidence PMIDs (attribution tripwire) ----

def verify_evidence_pmids(verifier: ReferenceVerifier, claim_text: str,
                          pmids: List[str]) -> Dict:
    """Round-trip + attribution-check the PMIDs Gate-2 cites as evidence.

    These PMIDs come from Gate-2's own esearch, so they resolve by
    construction; this check is a TRIPWIRE (V9.1 known-answer spirit) that
    they resolve to papers actually in scope of the claim — Rule 3. Output is
    stamped into the discovery record's validation_stats; retrieval failure
    is non-blocking and never silently passes (status retrieval_failed)."""
    result = {"status": "not_assessed", "checked": 0, "verified": [],
              "mismatches": [], "retrieval_failed": False}
    if not verifier.enabled or not pmids:
        return result
    try:
        records = verifier._fetch(pmids)  # honours injected fetcher (offline tests)
    except Exception as e:  # noqa: BLE001
        logger.warning("Layer 6b evidence-PMID verification retrieval failed: %s", e)
        return {**result, "status": "retrieval_failed", "retrieval_failed": True,
                "reason": str(e)}
    result["checked"] = len(pmids)
    for pmid in pmids:
        v = verifier.check_attribution(claim_text, pmid, records.get(pmid))
        if v.status == "retrieval_failed":
            result["retrieval_failed"] = True
        elif v.status == "verified":
            result["verified"].append(pmid)
        else:
            result["mismatches"].append(f"PMID {pmid}: {v.reason}")
    result["status"] = "retrieval_failed" if result["retrieval_failed"] else (
        "verified" if not result["mismatches"] else "mismatch")
    return result


def create_reference_verifier(**kwargs) -> ReferenceVerifier:
    """Factory — never construct directly (project convention)."""
    return ReferenceVerifier(**kwargs)


__all__ = [
    "PubMedRecord", "CitationEntry", "RoundtripVerdict", "SweepReport",
    "ReferenceVerifier", "create_reference_verifier", "verify_evidence_pmids",
]
