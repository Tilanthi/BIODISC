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
"""Tests for the real PubMed literature-novelty gate (Gate-2).

Network is never hit: a fake fetcher injects abstracts. Verifies the
novel/known/retrieval_failed logic and the §7.4 rule that transient failures
are never cached.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.literature_gate import (  # noqa: E402
    LiteratureNoveltyGate, create_literature_novelty_gate,
)


def _gate():
    return create_literature_novelty_gate(similarity_threshold=0.55)


def test_known_claim_is_flagged_known():
    """Claim sharing gene symbols + condition with an abstract -> entailed -> known."""
    gate = _gate()
    abstracts = [
        ("1", "TP53 mutations drive BRCA1 PARP inhibitor sensitivity in breast cancer tumors"),
    ]
    claim = "TP53 and BRCA1 regulate PARP inhibitor sensitivity in breast cancer"
    v = gate.assess(claim, fetcher=lambda q: abstracts)
    assert v.status == "known"
    assert v.max_similarity >= 0.55


def test_novel_claim_is_flagged_novel():
    """Claim with no overlapping gene symbols / terms -> not entailed -> novel."""
    gate = _gate()
    abstracts = [
        ("1", "Zinc finger homeostasis in Arabidopsis thaliana root development pathways"),
    ]
    claim = "XYZABC hypothetical locus controls mitochondrial cristae morphology in neurons"
    v = gate.assess(claim, fetcher=lambda q: abstracts)
    assert v.status == "novel"
    assert v.max_similarity < 0.55


def test_no_prior_literature_is_low_confidence_novel():
    gate = _gate()
    v = gate.assess("FOOBAR1 locus in quokka liver", fetcher=lambda q: [])
    assert v.status == "novel"
    assert v.n_papers_checked == 0


def test_retrieval_failure_is_not_cached():
    """§7.4: a transient retrieval failure must not be memoised — a later call re-checks."""
    gate = _gate()
    calls = {"n": 0}

    def flaky(query):
        calls["n"] += 1
        raise ConnectionError("transient")

    v1 = gate.assess("BRCA1 PARP inhibitor cancer", fetcher=flaky)
    assert v1.status == "retrieval_failed"
    # second call must retry (not return cached failure)
    v2 = gate.assess("BRCA1 PARP inhibitor cancer", fetcher=flaky)
    assert v2.status == "retrieval_failed"
    assert calls["n"] == 2  # retried both times


def test_successful_verdict_is_cached():
    gate = _gate()
    calls = {"n": 0}

    def fetcher(query):
        calls["n"] += 1
        return [("1", "TP53 BRCA1 breast cancer PARP")]

    gate.assess("TP53 BRCA1 breast cancer PARP", fetcher=fetcher)
    gate.assess("TP53 BRCA1 breast cancer PARP", fetcher=fetcher)
    assert calls["n"] == 1  # cached


def test_disabled_gate_returns_novel():
    gate = create_literature_novelty_gate(enabled=False)
    v = gate.assess("anything", fetcher=lambda q: (_ for _ in ()).throw(RuntimeError()))
    assert v.status == "novel"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
