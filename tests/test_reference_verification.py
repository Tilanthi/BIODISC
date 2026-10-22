"""Offline tests for the reference-verification gate (REFERENCE_VERIFICATION_PROTOCOL).

All PubMed fetches are injected (no network), mirroring tests/test_literature_gate.py.
Each test targets an observed audit failure mode: fabricated titles,
wrong-paper attribution, numeric digit drift, confabulated co-author lists,
invisible uncited entries.
"""
import pytest

from biodisc_core.fixed_pipeline.reference_verification import (
    CitationEntry, PubMedRecord, ReferenceVerifier,
    create_reference_verifier, verify_evidence_pmids,
)

REC = PubMedRecord(
    pmid="12345678",
    title="MTOR signaling drives resistance to BRAF inhibition in melanoma",
    authors=["Smith John", "Lee Sarah", "Patel Anil", "Chen Wei",
             "Garcia Maria", "Kim Daniel", "Novak Peter"],
    journal="Nature",
    year="2023",
    abstract="MTOR activation increased in BRAF inhibitor resistant melanoma. "
             "MTOR signaling drives resistance pathways and cell survival.",
)


def make_verifier(records=None, exc=None):
    def fetcher(pmids):
        if exc:
            raise exc
        return {r.pmid: r for r in (records or []) if r.pmid in pmids}
    return create_reference_verifier(fetcher=fetcher)


def entry(**kw):
    base = dict(key="smith2023",
                title=REC.title, authors=REC.authors[:3],
                journal=REC.journal, year=REC.year, pmid=REC.pmid)
    base.update(kw)
    return CitationEntry(**base)


class TestRoundtrip:
    def test_verified_on_exact_match(self):
        v = make_verifier([REC])
        verdict = v.verify_pmid_roundtrip(entry())
        assert verdict.status == "verified"
        assert verdict.title_similarity == pytest.approx(1.0)

    def test_fabricated_title_mismatch(self):
        # Failure mode #1: plausible fabricated title, right PMID.
        v = make_verifier([REC])
        verdict = v.verify_pmid_roundtrip(entry(
            title="A comprehensive catalogue of resistance mechanisms in cancer"))
        assert verdict.status == "mismatch"
        assert "different paper" in verdict.reason

    def test_digit_drift_pmid_unresolvable(self):
        # Failure mode #5: PMID 12345678 -> 12345878 does not resolve.
        v = make_verifier([REC])
        verdict = v.verify_pmid_roundtrip(entry(pmid="12345878"))
        assert verdict.status == "unresolvable"

    def test_confabulated_authors_mismatch(self):
        # Failure mode #4: right paper, zero author overlap.
        v = make_verifier([REC])
        verdict = v.verify_pmid_roundtrip(entry(
            authors=["Zimmer Fritz", "Aalborg Ulla", "Kowalski Jan"]))
        assert verdict.status == "mismatch"
        assert "author overlap" in verdict.reason

    def test_title_variant_ok_if_metadata_agrees(self):
        # Protocol Rule 2: sim in [0.5, 0.75) acceptable when journal+year agree.
        v = make_verifier([REC])
        verdict = v.verify_pmid_roundtrip(entry(
            title="MTOR signaling drives resistance to BRAF inhibition melanoma results"))
        assert verdict.status == "verified"

    def test_retrieval_failure_non_passing(self):
        v = make_verifier(exc=RuntimeError("network down"))
        verdict = v.verify_pmid_roundtrip(entry())
        assert verdict.status == "retrieval_failed"


class TestTranscription:
    def test_fields_transcribed_and_truncated_mechanically(self):
        v = make_verifier([REC])
        cite = v.build_citation(REC.pmid, max_authors=3)
        assert cite["title"] == REC.title
        assert cite["authors"] == ["Smith John", "Lee Sarah", "Patel Anil", "and others"]
        assert cite["full_author_count"] == 7
        assert cite["journal"] == "Nature" and cite["year"] == "2023"

    def test_cannot_transcribe_unresolvable_pmid(self):
        v = make_verifier([])
        with pytest.raises(ValueError, match="does not resolve"):
            v.build_citation("999")


class TestAttribution:
    def test_abstract_entails_claim(self):
        v = make_verifier([REC])
        verdict = v.check_attribution(
            "MTOR activation increases in BRAF inhibitor resistant melanoma", REC.pmid)
        assert verdict.status == "verified"

    def test_wrong_paper_attribution(self):
        # Failure mode #2: paper exists, claim belongs to a different one.
        v = make_verifier([REC])
        verdict = v.check_attribution(
            "Gut microbiome diversity predicts immunotherapy response in lung "
            "adenocarcinoma cohorts treated with anti-PD-L1 antibodies", REC.pmid)
        assert verdict.status == "mismatch"
        assert "does not entail" in verdict.reason


class TestSweep:
    def test_clean_sweep(self):
        v = make_verifier([REC])
        report = v.sweep_document(["smith2023"], [entry()])
        assert report.ok
        assert report.verified == ["smith2023"]
        assert not report.uncited_present and not report.exempt

    def test_cited_but_missing(self):
        v = make_verifier([REC])
        report = v.sweep_document(["smith2023", "jones2020"], [entry()])
        assert not report.ok
        assert report.cited_but_missing == ["jones2020"]

    def test_invisible_uncited_entry_flagged(self):
        # Failure mode #8: never-rendered entries survive without scrutiny.
        v = make_verifier([REC])
        report = v.sweep_document(["smith2023"],
                                  [entry(), entry(key="ghost2021", title="Fake entry")])
        assert report.ok  # not a hard failure — but must be reported (Rule 8)
        assert report.uncited_present == ["ghost2021"]
        assert "ghost2021" in report.summary()

    def test_exempt_and_no_pmid_reported(self):
        v = make_verifier([REC])
        report = v.sweep_document(
            ["smith2023", "book1", "misc1"],
            [entry(), entry(key="book1", title="Some Book", pmid="",
                            exempt_reason="book — verify by hand"),
             entry(key="misc1", title="Software", pmid="")])
        assert report.verified == ["smith2023"]
        assert len(report.exempt) == 2
        assert any("book" in e for e in report.exempt)
        assert any("no PMID" in e for e in report.exempt)

    def test_sweep_retrieval_failure_fails_not_passes(self):
        v = make_verifier(exc=RuntimeError("down"))
        report = v.sweep_document(["smith2023"], [entry()])
        assert not report.ok
        assert report.retrieval_failed == ["smith2023"]


class TestEvidencePmidHook:
    def test_verified(self):
        v = make_verifier([REC])
        out = verify_evidence_pmids(
            v, "MTOR increases in BRAF resistant melanoma", [REC.pmid])
        assert out["status"] == "verified"
        assert out["verified"] == [REC.pmid]

    def test_mismatch(self):
        v = make_verifier([REC])
        out = verify_evidence_pmids(
            v, "Photosystem II repair cycles in cyanobacteria under high light", [REC.pmid])
        assert out["status"] == "mismatch"
        assert out["mismatches"]

    def test_retrieval_failed_non_blocking_and_honest(self):
        v = make_verifier(exc=RuntimeError("down"))
        out = verify_evidence_pmids(v, "anything", ["1"])
        assert out["status"] == "retrieval_failed"
        assert out["retrieval_failed"] is True

    def test_disabled_verifier_not_assessed(self):
        v = ReferenceVerifier(enabled=False)
        assert verify_evidence_pmids(v, "x", ["1"])["status"] == "not_assessed"
