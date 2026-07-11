"""B.3 + B.4 — discovery status/heartbeat + flagging gate."""
import time

import biodisc_core.fixed_pipeline.discovery_status as status
from biodisc_core.fixed_pipeline.discovery_gate import (
    evaluate_for_flagging, stamp_report, TIER_GENUINE, TIER_CANDIDATE, TIER_REJECTED,
)


# --- discovery_status ---

def test_status_records(tmp_path, monkeypatch):
    monkeypatch.setattr(status, "STATUS_FILE", tmp_path / "status.json")
    monkeypatch.setattr(status, "HEARTBEAT_FILE", tmp_path / "hb")

    assert status.seconds_since_validated_discovery() is None
    status.record_cycle(3)
    status.record_validated_discovery("DISC_1")
    status.record_rejection("no_datasets")
    status.record_rejection("no_datasets")
    status.record_rejection("validation_failed")

    s = status.read_status()
    assert s["last_cycle_discoveries"] == 3
    assert s["validated_count"] == 1
    assert s["rejections"]["no_datasets"] == 2
    assert s["rejections"]["validation_failed"] == 1
    assert status.seconds_since_validated_discovery() is not None


def test_heartbeat_user_active(tmp_path, monkeypatch):
    monkeypatch.setattr(status, "HEARTBEAT_FILE", tmp_path / "hb")
    assert status.is_user_active() is False  # no heartbeat -> not active -> loop runs
    status.touch_heartbeat()
    assert status.is_user_active() is True
    # Simulate a stale heartbeat (mtime in the past beyond the window)
    import os
    old = time.time() - 1000
    os.utime(tmp_path / "hb", (old, old))
    assert status.is_user_active() is False


# --- discovery_gate (the honest "check before flagging") ---

def test_single_dataset_discovery_is_candidate_not_genuine():
    report = {"comprehensive_validation_statistics": {"x": {"passed": True}}}
    d = evaluate_for_flagging(report)
    assert d.tier == TIER_CANDIDATE
    assert d.is_genuine is False  # no replication -> never flagged genuine


def test_replicated_discovery_becomes_genuine():
    report = {"replication": {"replicated": True}, "peer_review_result": {"decision": "ACCEPT"}}
    d = evaluate_for_flagging(report)
    assert d.tier == TIER_GENUINE
    assert d.is_genuine is True


def test_peer_rejected_is_rejected():
    report = {"peer_review_result": {"decision": "REJECT"}, "replication": {"replicated": True}}
    assert evaluate_for_flagging(report).tier == TIER_REJECTED


def test_failed_validation_layer_is_rejected():
    report = {"comprehensive_validation_statistics": {"fdr": {"passes_significance_gate": False}}}
    assert evaluate_for_flagging(report).tier == TIER_REJECTED


def test_stamp_report_marks_not_genuine_by_default():
    out, decision = stamp_report({"comprehensive_validation_statistics": {}})
    assert out["is_genuine"] is False
    assert out["flagging"]["tier"] == TIER_CANDIDATE
    assert "not flagged genuine" in out["flagging"]["reason"]
