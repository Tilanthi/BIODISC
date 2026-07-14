"""Regression tests for the discovery-store write chokepoint.

This is BIODISC's defence against its #1 enemy — fictional/hallucinated
discoveries (the known LLM-in-biology failure mode). Mirrors ASTRA's
`test_discovery_chokepoint.py`: there must be exactly ONE write path to the
discovery store, and it must require a machine `verification` block carrying
objective real-data evidence. Fiction must be STRUCTURALLY IMPOSSIBLE.

Run: python -m pytest tests/test_discovery_chokepoint.py -v
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.discovery_store import (  # noqa: E402
    append_verified,
    has_machine_verification,
    UnverifiedDiscoveryError,
    VERIFIED_STORE,
    CANDIDATE_QUARANTINE,
)


def _verification(dataset_id="GSE12345", **extra):
    """A well-formed machine verification block (objective real-data evidence)."""
    block = {
        "pipeline": "fixed_pipeline_v6",
        "pipeline_hash": "fixed_v6|ttest|bhfdr",
        "real_data_result": {
            "dataset_id": dataset_id,
            "n_significant_genes": 12,
            "min_fdr": 0.001,
            "method": "ttest+bh_fdr",
        },
        "gates": {
            "duplicate": True,
            "dataset_question": True,
            "probe_gene": True,
            "fdr_significance": True,
            "template": True,
            "literature_novelty": "novel",
            "replication": True,
        },
        "verified_at": "2026-07-14T00:00:00",
    }
    block.update(extra)
    return block


# --- has_machine_verification -------------------------------------------------

def test_fictional_record_without_verification_block_is_rejected():
    """ASTRA's darkest finding: a hardcoded string written as a 'discovery'."""
    fictional = {"discovery_id": "FAKE_1", "claim": "Gene X causes cancer"}
    assert has_machine_verification(fictional) is False


def test_verification_block_missing_real_data_result_is_rejected():
    rec = {"verification": {"pipeline_hash": "x", "gates": {}}}
    assert has_machine_verification(rec) is False


def test_real_data_result_without_dataset_id_is_rejected():
    rec = {"verification": {"real_data_result": {"n_significant_genes": 5}, "gates": {}}}
    assert has_machine_verification(rec) is False


def test_well_formed_verification_passes():
    rec = {"verification": _verification()}
    assert has_machine_verification(rec) is True


# --- append_verified: the single write path ----------------------------------

def test_append_without_verification_raises(tmp_path):
    rec = {"discovery_id": "D1", "flagging": {"tier": "genuine"}}
    with pytest.raises(UnverifiedDiscoveryError):
        append_verified(rec, verification=None, store_dir=tmp_path)


def test_append_with_incomplete_verification_raises(tmp_path):
    rec = {"discovery_id": "D1", "flagging": {"tier": "genuine"}}
    with pytest.raises(UnverifiedDiscoveryError):
        append_verified(rec, verification={"pipeline_hash": "x", "gates": {}}, store_dir=tmp_path)


def test_genuine_replicated_record_goes_to_verified_store(tmp_path):
    rec = {
        "discovery_id": "D_GEN",
        "flagging": {"tier": "genuine", "is_genuine": True},
        "is_genuine": True,
    }
    target = append_verified(rec, verification=_verification(), store_dir=tmp_path)
    assert Path(target) == tmp_path / VERIFIED_STORE.name
    line = json.loads((tmp_path / VERIFIED_STORE.name).read_text().strip())
    assert line["discovery_id"] == "D_GEN"
    assert has_machine_verification(line) is True
    # candidate quarantine must be empty
    assert not (tmp_path / CANDIDATE_QUARANTINE.name).exists()


def test_candidate_unconfirmed_goes_to_quarantine_not_verified_store(tmp_path):
    """Single-cohort findings are machine-verified but NOT replicated: they must
    be quarantined, never admitted to the headline verified store."""
    rec = {
        "discovery_id": "D_CAND",
        "flagging": {"tier": "candidate_unconfirmed", "is_genuine": False},
        "is_genuine": False,
    }
    target = append_verified(rec, verification=_verification(), store_dir=tmp_path)
    assert Path(target) == tmp_path / CANDIDATE_QUARANTINE.name
    assert not (tmp_path / VERIFIED_STORE.name).exists()
    line = json.loads((tmp_path / CANDIDATE_QUARANTINE.name).read_text().strip())
    assert has_machine_verification(line) is True


def test_rejected_tier_is_never_stored(tmp_path):
    rec = {"discovery_id": "D_REJ", "flagging": {"tier": "rejected", "is_genuine": False}}
    with pytest.raises(UnverifiedDiscoveryError):
        append_verified(rec, verification=_verification(), store_dir=tmp_path)


def test_fictional_astra_style_record_cannot_be_stored(tmp_path):
    """The exact failure ASTRA suffered: a hardcoded string emitted ~60/hour.
    No code path may write such a record, because every path goes through the
    chokepoint, and the chokepoint demands a verification block."""
    fictional = {"discovery_id": "HARDCODED", "finding": "placeholder discovery string"}
    with pytest.raises(UnverifiedDiscoveryError):
        append_verified(fictional, verification=None, store_dir=tmp_path)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
