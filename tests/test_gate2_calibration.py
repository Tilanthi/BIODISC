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
"""Tests for Gate-2 truth-set calibration (V9.1, Paper2Agent lesson #2b).

The gate that guards novelty must itself be MEASURED, not assumed. The truth
set has two sides with different jobs:

* known side — real textbook claims that MUST score ``known`` (catches an
  over-permissive gate letting textbook biology through as "novel").
* novel side — seeded from the genuine store's own questions (regression:
  catches threshold drift that would kill findings the store already verified).

All tests here are OFFLINE (injected fetchers / fake gates). The live run
(``--live``) hits real PubMed and is operator-invoked.

Run: python -m pytest tests/test_gate2_calibration.py -v
"""
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline import gate2_calibration as g2c  # noqa: E402


# --------------------------------------------------------------------- fakes
class FakeGate:
    """stand-in LiteratureNoveltyGate with a scripted verdict map."""

    def __init__(self, verdicts):
        self.verdicts = verdicts  # claim -> status

    def assess(self, claim_text, question=None, fetcher=None):
        return NS(status=self.verdicts.get(claim_text, "novel"), max_similarity=0.3)


# ------------------------------------------------------------------ truth set
def test_truth_set_loads_with_known_claims():
    ts = g2c.load_truth_set()
    assert len(ts["known_claims"]) >= 20
    for kc in ts["known_claims"]:
        assert kc["claim"].strip()
        assert kc["basis"]
    # spot-check real textbook entries
    claims = " || ".join(kc["claim"] for kc in ts["known_claims"])
    assert "TP53" in claims and "BCL2" in claims and "SOD1" in claims


def test_derive_novel_claims_reads_store(tmp_path):
    store = tmp_path / "autonomous_discoveries.jsonl"
    recs = [
        {"question": "Whereas MYC typically increases, does it decrease here?", "flagging": {"tier": "genuine"}},
        {"question": "Does MTOR decrease in fatty liver?", "flagging": {"tier": "genuine"}},
        {"question": "candidate question (must be excluded)", "flagging": {"tier": "candidate_unconfirmed"}},
    ]
    store.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    claims = g2c.derive_novel_claims(store_path=store)
    # most recent first (the store appends, so the last line is newest)
    assert claims == ["Does MTOR decrease in fatty liver?",
                      "Whereas MYC typically increases, does it decrease here?"]


def test_derive_novel_claims_caps_and_skips_blank(tmp_path):
    store = tmp_path / "autonomous_discoveries.jsonl"
    recs = [{"question": f"genuine q{i}", "flagging": {"tier": "genuine"}} for i in range(20)]
    recs.append({"question": "", "flagging": {"tier": "genuine"}})
    store.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    claims = g2c.derive_novel_claims(store_path=store, cap=12)
    assert len(claims) == 12
    assert all(claims)


# ------------------------------------------------------------------ evaluate
def test_evaluate_scoring_math():
    known = ["k1", "k2", "k3", "k4"]
    novel = ["n1", "n2"]
    gate = FakeGate({k: "known" for k in known} | {n: "novel" for n in novel})
    res = g2c.evaluate(gate, known, novel)
    assert res["known_accuracy"] == 1.0
    assert res["novel_accuracy"] == 1.0
    assert res["n_known"] == 4 and res["n_novel"] == 2
    assert res["retrieval_failures"] == 0


def test_evaluate_counts_errors():
    known = ["k1", "k2", "k3", "k4"]
    novel = ["n1", "n2", "n3", "n4"]
    gate = FakeGate({  # one wrong each side, the rest correct
        "k1": "known", "k2": "novel", "k3": "known", "k4": "known",
        "n1": "novel", "n2": "novel", "n3": "known", "n4": "novel",
    })
    res = g2c.evaluate(gate, known, novel)
    assert res["known_accuracy"] == 0.75
    assert res["novel_accuracy"] == 0.75
    wrong = [p for p in res["per_claim"] if p["got"] != p["expected"]]
    assert {p["claim"] for p in wrong} == {"k2", "n3"}


def test_retrieval_failures_not_counted():
    known = ["k1", "k2"]
    novel = ["n1", "n2"]
    gate = FakeGate({"k1": "known", "k2": "retrieval_failed", "n1": "retrieval_failed", "n2": "novel"})
    res = g2c.evaluate(gate, known, novel)
    assert res["retrieval_failures"] == 2
    assert res["n_known"] == 1 and res["n_novel"] == 1
    assert res["known_accuracy"] == 1.0 and res["novel_accuracy"] == 1.0


# ------------------------------------------------- real gate, offline fetcher
def test_entailing_abstract_scores_known():
    from biodisc_core.fixed_pipeline.literature_gate import create_literature_novelty_gate
    gate = create_literature_novelty_gate()
    claim = "TP53 is the most frequently mutated gene in human cancer"
    entailing = ("1", "TP53 is the most frequently mutated gene in human cancer. "
                      "Mutation of TP53 loss of function occurs in more than half of "
                      "human cancers, making TP53 the most frequently altered tumor "
                      "suppressor gene in human cancer.")
    verdict = gate.assess(claim, fetcher=lambda q: [entailing])
    assert verdict.status == "known", (
        f"entailing abstract scored {verdict.status} (sim={verdict.max_similarity:.2f}) — "
        "Gate-2 lets textbook through")


def test_unrelated_abstract_scores_novel():
    from biodisc_core.fixed_pipeline.literature_gate import create_literature_novelty_gate
    gate = create_literature_novelty_gate()
    claim = "XYZNOVEL1 shows an unexpectedly large downregulated change"
    unrelated = ("1", "Photosynthesis in cyanobacteria relies on light-harvesting "
                      "complexes that transfer excitation energy to reaction centers.")
    verdict = gate.assess(claim, fetcher=lambda q: [unrelated])
    assert verdict.status == "novel"


def test_offline_selfcheck_run(tmp_path, monkeypatch):
    monkeypatch.setattr(g2c, "REPORT_FILE", tmp_path / "gate2_calibration_report.json")
    report = g2c.run(live=False, write=True)
    saved = json.loads((tmp_path / "gate2_calibration_report.json").read_text())
    assert saved["mode"] == "offline_selfcheck"
    assert "fetcher_injected" in saved


@pytest.mark.skipif(not os.environ.get("BIODISC_GATE2_LIVE"),
                    reason="live PubMed run is operator-invoked (BIODISC_GATE2_LIVE=1)")
def test_live_calibration():
    report = g2c.run(live=True, write=False)
    assert report["mode"] == "live"
    assert report["n_known"] >= 20
    print(json.dumps(report["summary"], indent=2))
