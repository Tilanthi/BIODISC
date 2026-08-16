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
"""P3.3 + P3.4 — publication gate + advisory soft signals."""
from biodisc_core.evolution.publication import (
    PublicationGate, publish_discovery, GenealogyNode,
    PUBLISH_ELIGIBLE, HOLD_FOR_REVIEW, REJECT,
)
from biodisc_core.evolution.replication import ReplicationScore
from biodisc_core.evolution.soft_signals import grade_soft_signals, SoftSignals


def _score(rep, prec, n=10):
    return ReplicationScore(replication_rate=rep, precision=prec, n_claims=n,
                            aggregate=0.7 * rep + 0.3 * prec)


# --- PublicationGate ---

def test_gate_publish_eligible():
    g = PublicationGate()
    d = g.evaluate(_score(0.8, 0.7))
    assert d.decision == PUBLISH_ELIGIBLE


def test_gate_hold_for_review():
    g = PublicationGate()
    d = g.evaluate(_score(0.55, 0.4))
    assert d.decision == HOLD_FOR_REVIEW


def test_gate_reject_low_replication():
    g = PublicationGate()
    assert g.evaluate(_score(0.2, 0.6)).decision == REJECT


def test_gate_reject_too_few_claims():
    g = PublicationGate()
    d = g.evaluate(ReplicationScore(0.9, 0.9, n_claims=1, aggregate=0.9))
    assert d.decision == REJECT and "few claims" in d.reason


# --- publish_discovery human checkpoint ---

def _genealogy():
    return [GenealogyNode(program_id="child1", parent_id="seed", aggregate=0.8, generation=1)]


def test_publish_dry_run_without_human_approval(tmp_path):
    log = tmp_path / "pub.jsonl"
    rec = publish_discovery(
        discovery_program_id="dp1", discovery_program_source="def discover(...):...",
        method_program_id="m1", cohort_id="cohort_a",
        score=_score(0.8, 0.7),
        decision=PublicationGate().evaluate(_score(0.8, 0.7)),
        claims=[{"gene_index": 1}],
        genealogy=_genealogy(),
        human_approved=False, log_path=str(log),
    )
    assert rec.written is False
    assert rec.decision == PUBLISH_ELIGIBLE
    assert not log.exists()  # nothing written without human approval


def test_publish_writes_with_human_approval(tmp_path):
    log = tmp_path / "pub.jsonl"
    decision = PublicationGate().evaluate(_score(0.8, 0.7))
    rec = publish_discovery(
        discovery_program_id="dp1", discovery_program_source="def discover(...):...",
        method_program_id="m1", cohort_id="cohort_a",
        score=_score(0.8, 0.7), decision=decision,
        claims=[{"gene_index": 1, "direction": 1}],
        genealogy=_genealogy(),
        human_approved=True, log_path=str(log),
    )
    assert rec.written is True
    assert log.exists()
    # The written record carries full provenance.
    line = log.read_text().strip().splitlines()[-1]
    import json
    obj = json.loads(line)
    assert obj["discovery_program_id"] == "dp1"
    assert obj["method_program_id"] == "m1"
    assert obj["genealogy"][0]["parent_id"] == "seed"


def test_publish_never_writes_on_reject(tmp_path):
    log = tmp_path / "pub.jsonl"
    decision = PublicationGate().evaluate(_score(0.2, 0.4))  # REJECT
    rec = publish_discovery(
        discovery_program_id="dp1", discovery_program_source="...",
        method_program_id=None, cohort_id="cohort_a",
        score=_score(0.2, 0.4), decision=decision, claims=[],
        genealogy=[], human_approved=True, log_path=str(log),
    )
    assert rec.written is False
    assert not log.exists()


# --- Soft signals (advisory, non-anchoring) ---

def test_soft_signals_parse_json():
    proposer = lambda s, u: '{"novelty": 0.8, "literature_consistency": 0.6, "rationale": "ok"}'  # noqa: E731
    sig = grade_soft_signals("BRCA1 loss ...", proposer)
    assert isinstance(sig, SoftSignals)
    assert sig.novelty == 0.8
    assert sig.literature_consistency == 0.6
    assert sig.is_anchor is False


def test_soft_signals_clamp_and_garbage_safe():
    proposer = lambda s, u: "this is not json at all"  # noqa: E731
    sig = grade_soft_signals("claim", proposer)
    assert sig.novelty == 0.0
    assert sig.literature_consistency == 0.0
    assert sig.is_anchor is False


def test_soft_signals_proposer_failure_is_safe():
    def bad(s, u):
        raise RuntimeError("api down")
    sig = grade_soft_signals("claim", bad)
    assert sig.novelty == 0.0 and "unavailable" in sig.rationale
