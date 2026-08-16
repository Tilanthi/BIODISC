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
"""Tests for the contrarian-success-rate metric (rebuild item 5)."""
import json

from biodisc_core.fixed_pipeline.capability_index import contrarian_success_rate


def _write_log(tmp_path, entries):
    p = tmp_path / "v.jsonl"
    with open(p, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return p


def test_metric_counts_supported_and_novel(tmp_path):
    log = _write_log(tmp_path, [
        {"question": "q1", "gene_hypothesis_supports": True, "gate2_status": "novel"},   # surprise
        {"question": "q2", "gene_hypothesis_supports": True, "gate2_status": "known"},   # supported but known
        {"question": "q3", "gene_hypothesis_supports": False, "gate2_status": "novel"},  # failed contrarian
        {"question": "q4"},  # exploratory -> skipped
    ])
    m = contrarian_success_rate(log)
    assert m["contrarian_tested"] == 3
    assert m["supported"] == 2
    assert m["supported_and_novel"] == 1
    assert m["supported_but_known"] == 1
    assert m["supported_novel_rate"] == round(1 / 3, 4)


def test_metric_empty_when_no_gene_hypothesis(tmp_path):
    log = _write_log(tmp_path, [{"question": "q"}, {"question": "q2"}])
    m = contrarian_success_rate(log)
    assert m["contrarian_tested"] == 0
    assert m["supported_novel_rate"] == 0.0


def test_metric_handles_missing_file(tmp_path):
    m = contrarian_success_rate(tmp_path / "does_not_exist.jsonl")
    assert m["contrarian_tested"] == 0
    assert m["supported_novel_rate"] == 0.0
