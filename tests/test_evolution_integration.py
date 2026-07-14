"""Tests for the supervised evolution integration (Step 6).

Uses a fake controller so no LLM endpoint / network is required. Verifies the
wiring (result mapping) and the dry-run vs publish distinction.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import biodisc_core.fixed_pipeline.evolution_integration as ei  # noqa: E402


class _FakeScore:
    aggregate = 0.70
    replication_rate = 0.70
    precision = 1.00


class _FakeBest:
    aggregate = 0.80
    replicate_concordance = 0.80
    auroc = 0.90


class _FakeAttempt:
    def __init__(self, accepted):
        self.accepted = accepted


class _FakeRecord:
    def __init__(self, written):
        self.written = written


class _FakeDecision:
    def __init__(self, decision):
        self.decision = decision


class _FakeDB:
    @staticmethod
    def all_programs():
        return [1, 2, 3, 4, 5]


class _FakeCtrl:
    def __init__(self, *args, **kwargs):
        self.attempts = [_FakeAttempt(True), _FakeAttempt(True), _FakeAttempt(False)]
        self.seed_score = _FakeScore()
        self.db = _FakeDB()

    def run(self, **kwargs):
        return _FakeBest()

    def publish_best(self, human_approved=False):
        return _FakeRecord(human_approved), _FakeScore(), _FakeDecision("PUBLISH_ELIGIBLE"), None


def test_dry_run_does_not_publish(monkeypatch):
    monkeypatch.setattr(ei, "DiscoveryEvolutionController", _FakeCtrl)
    r = ei.run_method_evolution(generations=1)
    assert r.ran is True
    assert r.best_aggregate == 0.8
    assert r.accepted == 2
    assert r.rejected == 1
    assert r.genealogy_size == 5
    assert r.publication_decision == "PUBLISH_ELIGIBLE"
    assert r.publication_written is False  # dry run


def test_publish_flag_writes(monkeypatch):
    monkeypatch.setattr(ei, "DiscoveryEvolutionController", _FakeCtrl)
    r = ei.run_method_evolution(generations=1, publish=True)
    assert r.publication_written is True


def test_failure_is_graceful(monkeypatch):
    class _Boom:
        def __init__(self, *a, **k):
            raise RuntimeError("no LLM endpoint configured")
    monkeypatch.setattr(ei, "DiscoveryEvolutionController", _Boom)
    r = ei.run_method_evolution(generations=1)
    assert r.ran is False
    assert r.error is not None
    assert "no LLM endpoint" in r.error


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
