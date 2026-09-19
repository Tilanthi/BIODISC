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
"""Tests for the real-data known-answer control suite (V9.1, Paper2Agent lesson #1).

The pipeline must RECOVER what it already verified: each control case is a
genuine-store finding (dataset + verified genes + directions), and the runner
re-runs the REAL DE analyzer on resolved data and checks the genes come back
same-direction + significant. This is the tripwire for wiring bugs the
synthetic benchmark can't see (GPL probe->gene mapping; the V8.0.34 orientation
bug where the gene-specific test silently never ran).

Paper2Agent-style status ladder — failures are LABELED, never silently green:
PASS | FAIL_DIRECTION | FAIL_SIGNIFICANCE | FAIL_ABSENT | SKIP_NO_DATA | ERROR.

Offline: tests use synthetic expression arrays through the REAL analyzer
(test scaffolding, never stored as discoveries).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.known_answer_controls import cases as kac  # noqa: E402
from biodisc_core.fixed_pipeline.known_answer_controls import runner as kar  # noqa: E402
from biodisc_core.fixed_pipeline.differential_expression import (  # noqa: E402
    create_differential_expression_analyzer,
)


# --------------------------------------------------------------- data builder
def _make_data(n_genes=40, n_per_group=8, seed=3):
    """genes x samples expression; GENE_A strongly up in group 1, GENE_B down."""
    rng = np.random.default_rng(seed)
    symbols = [f"G{i:03d}" for i in range(n_genes)]
    if "GENE_A" not in symbols:
        symbols[0] = "GENE_A"
    if "GENE_B" not in symbols:
        symbols[1] = "GENE_B"
    # realistic expression values: positive (raw or log2 space), so the
    # analyzer's log-ratio path is well-defined (negative scaffolds give nan)
    X = rng.normal(8.0, 0.5, size=(n_genes, 2 * n_per_group))
    ia, ib = symbols.index("GENE_A"), symbols.index("GENE_B")
    # analyzer convention: positive log2FC = higher in label-1 (treatment)
    X[ia, n_per_group:] += 2.0     # GENE_A up (in label 1)
    X[ib, :n_per_group] += 2.0     # GENE_B down (high in label 0)
    labels = np.array([0] * n_per_group + [1] * n_per_group)
    return X, symbols, labels


def _case(genes, dataset_id="TESTDS", question="control contrast"):
    return kac.KnownAnswerCase(
        case_id=f"{dataset_id}:ctrl", dataset_id=dataset_id, question=question,
        genes=genes, source="genuine_store", discovery_id="D-TEST",
        seeded_at="2026-09-19T00:00:00+00:00")


# --------------------------------------------------------------------- cases
def test_seed_from_genuine_store(tmp_path):
    store = tmp_path / "autonomous_discoveries.jsonl"
    genuine = {
        "discovery_id": "D1", "question": "q1",
        "dataset": {"geo_id": "GSE1"},
        "differential_expression": {
            "top_upregulated": [
                {"gene_symbol": "AAA", "log2_fold_change": 1.1, "fdr_p_value": 1e-5, "regulation": "up"},
                {"gene_symbol": "BBB", "log2_fold_change": 0.9, "fdr_p_value": 1e-4, "regulation": "up"},
            ],
            "top_downregulated": [
                {"gene_symbol": "CCC", "log2_fold_change": -1.2, "fdr_p_value": 1e-6, "regulation": "down"},
            ],
        },
        "replication": {"replicated": True},
        "flagging": {"tier": "genuine"},
    }
    candidate = dict(genuine, discovery_id="D2", flagging={"tier": "candidate_unconfirmed"})
    store.write_text(json.dumps(genuine) + "\n" + json.dumps(candidate) + "\n")
    cases = kac.seed_from_genuine_store(store_path=store)
    assert len(cases) == 1, "candidate-tier records must not seed controls"
    c = cases[0]
    assert c.dataset_id == "GSE1" and c.discovery_id == "D1"
    assert {g["symbol"] for g in c.genes} == {"AAA", "BBB", "CCC"}
    dirs = {g["symbol"]: g["direction"] for g in c.genes}
    assert dirs["AAA"] == "up" and dirs["CCC"] == "down"


def test_seed_caps_genes_per_case(tmp_path):
    store = tmp_path / "autonomous_discoveries.jsonl"
    rec = {
        "discovery_id": "D1", "question": "q1", "dataset": {"geo_id": "GSE1"},
        "differential_expression": {
            "top_upregulated": [{"gene_symbol": f"UP{i}", "log2_fold_change": 1.0,
                                 "fdr_p_value": 1e-5, "regulation": "up"} for i in range(20)],
            "top_downregulated": [],
        },
        "replication": {"replicated": True},
        "flagging": {"tier": "genuine"},
    }
    store.write_text(json.dumps(rec) + "\n")
    cases = kac.seed_from_genuine_store(store_path=store)
    assert len(cases[0].genes) <= 5


def test_seed_dedups_same_contrast(tmp_path):
    """Two genuine records from the same dataset with the same top genes are ONE
    control case, not two (the live store has 3-4 such repeats per contrast)."""
    store = tmp_path / "autonomous_discoveries.jsonl"
    base = {
        "question": "q", "dataset": {"geo_id": "GSE1"},
        "differential_expression": {
            "top_upregulated": [{"gene_symbol": "AAA", "log2_fold_change": 1.5,
                                 "fdr_p_value": 1e-5, "regulation": "up"}],
            "top_downregulated": [],
        },
        "replication": {"replicated": True},
        "flagging": {"tier": "genuine"},
    }
    dup1 = dict(base, discovery_id="D1")
    dup2 = dict(base, discovery_id="D2")  # same contrast, same genes
    store.write_text(json.dumps(dup1) + "\n" + json.dumps(dup2) + "\n")
    cases = kac.seed_from_genuine_store(store_path=store)
    assert len(cases) == 1


def test_save_and_load_cases_roundtrip(tmp_path):
    p = tmp_path / "known_answer_cases.json"
    c = _case([{"symbol": "GENE_A", "direction": "up", "log2fc": 1.5, "fdr": 1e-6}])
    kac.save_cases([c], p)
    loaded = kac.load_cases(p)
    assert loaded == [c]


# --------------------------------------------------------------------- runner
def test_run_controls_pass_on_recovering_data():
    X, symbols, labels = _make_data()
    case = _case([
        {"symbol": "GENE_A", "direction": "up", "log2fc": 2.0, "fdr": 1e-8},
        {"symbol": "GENE_B", "direction": "down", "log2fc": -2.0, "fdr": 1e-8},
    ])
    report = kar.run_controls(
        [case],
        data_resolver=lambda c: (X, symbols, labels),
        analyzer=create_differential_expression_analyzer())
    r = report["results"][0]
    assert r["status"] == "PASS", r
    assert report["summary"]["pass"] == 1 and report["pass_rate"] == 1.0


def test_fail_direction_when_flipped():
    X, symbols, labels = _make_data()
    case = _case([{"symbol": "GENE_A", "direction": "down", "log2fc": -2.0, "fdr": 1e-8}])
    report = kar.run_controls(
        [case],
        data_resolver=lambda c: (X, symbols, labels),
        analyzer=create_differential_expression_analyzer())
    assert report["results"][0]["status"] == "FAIL_DIRECTION"


def test_fail_absent_when_gene_missing():
    X, symbols, labels = _make_data()
    case = _case([{"symbol": "NOT_THERE", "direction": "up", "log2fc": 1.0, "fdr": 1e-5}])
    report = kar.run_controls(
        [case],
        data_resolver=lambda c: (X, symbols, labels),
        analyzer=create_differential_expression_analyzer())
    assert report["results"][0]["status"] == "FAIL_ABSENT"


def test_skip_no_data_on_resolver_error():
    case = _case([{"symbol": "GENE_A", "direction": "up", "log2fc": 1.0, "fdr": 1e-5}])

    def boom(c):
        raise TimeoutError("download bounded out")

    report = kar.run_controls([case], data_resolver=boom,
                              analyzer=create_differential_expression_analyzer())
    assert report["results"][0]["status"] == "SKIP_NO_DATA"
    assert report["summary"]["skip"] == 1


def test_report_written_and_capability_index_ingests(tmp_path, monkeypatch):
    from biodisc_core.fixed_pipeline import capability_index as ci
    report_path = tmp_path / "known_answer_report.json"
    monkeypatch.setattr(kar, "REPORT_FILE", report_path)
    X, symbols, labels = _make_data()
    case = _case([{"symbol": "GENE_A", "direction": "up", "log2fc": 2.0, "fdr": 1e-8}])
    report = kar.run_controls([case], data_resolver=lambda c: (X, symbols, labels),
                              analyzer=create_differential_expression_analyzer(),
                              write=True)
    assert report_path.exists()
    monkeypatch.setattr(ci, "KNOWN_ANSWER_REPORT", report_path)
    block = ci.read_known_answer_block()
    assert block is not None
    assert block["pass_rate"] == 1.0 and block["n_pass"] == 1
