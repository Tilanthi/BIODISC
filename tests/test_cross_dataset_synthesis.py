"""Tests for cross-dataset module synthesis."""
import json
from pathlib import Path

from biodisc_core.fixed_pipeline.cross_dataset_synthesis import (
    load_gene_directions, find_bridges, find_shared, anomaly_vs_expectation, summarize)


def _write_store(tmp_path: Path, discoveries: list) -> Path:
    p = tmp_path / "store.jsonl"
    with open(p, "w") as f:
        for d in discoveries:
            f.write(json.dumps(d) + "\n")
    return p


def _disc(gse, ups, downs, question="Q"):
    return {
        "is_genuine": True,
        "question": question,
        "dataset": {"geo_id": gse},
        "differential_expression": {
            "top_upregulated": [{"gene_symbol": g, "regulation": "up"} for g in ups],
            "top_downregulated": [{"gene_symbol": g, "regulation": "down"} for g in downs],
        },
    }


def test_bridge_detection_finds_direction_flip(tmp_path):
    store = _write_store(tmp_path, [
        _disc("GSE1", ups=["GENEA", "GENEB"], downs=[]),
        _disc("GSE2", ups=["GENEB"], downs=["GENEA"]),   # GENEA flips up->down
    ])
    dirs = load_gene_directions(store)
    bridges = {b.gene: b for b in find_bridges(dirs)}
    assert "GENEA" in bridges and bridges["GENEA"].is_flip
    assert bridges["GENEA"].up_in == ["GSE1"]
    assert bridges["GENEA"].down_in == ["GSE2"]
    # GENEB is up in both -> consistent, NOT a bridge
    assert "GENEB" not in bridges


def test_shared_modules_finds_consistent_gene(tmp_path):
    store = _write_store(tmp_path, [
        _disc("GSE1", ups=["GENEB"], downs=[]),
        _disc("GSE2", ups=["GENEB"], downs=[]),
        _disc("GSE3", ups=["GENEB"], downs=[]),
    ])
    dirs = load_gene_directions(store)
    shared = find_shared(dirs, min_datasets=3)
    assert shared and shared[0][0] == "GENEB" and shared[0][1] == "up" and shared[0][2] == 3


def test_single_dataset_gene_is_not_a_bridge(tmp_path):
    store = _write_store(tmp_path, [_disc("GSE1", ups=["LONE"], downs=[])])
    dirs = load_gene_directions(store)
    assert find_bridges(dirs) == []


def test_anomaly_inert_without_baseline(tmp_path):
    store = _write_store(tmp_path, [_disc("GSE1", ups=["X"], downs=[])])
    dirs = load_gene_directions(store)
    assert anomaly_vs_expectation(dirs, expected_baseline=None) == []


def test_only_genuine_counted_by_default(tmp_path):
    store = _write_store(tmp_path, [
        {"is_genuine": True, "dataset": {"geo_id": "GSE1"},
         "differential_expression": {"top_upregulated": [{"gene_symbol": "G", "regulation": "up"}]}},
        {"is_genuine": False, "dataset": {"geo_id": "GSE2"},
         "differential_expression": {"top_upregulated": [{"gene_symbol": "G", "regulation": "down"}]}},
    ])
    dirs = load_gene_directions(store)                      # default: genuine only
    assert "GSE2" not in dirs.get("G", {})
    dirs2 = load_gene_directions(store, include_candidates=True)
    assert "GSE2" in dirs2.get("G", {})                     # candidates included
