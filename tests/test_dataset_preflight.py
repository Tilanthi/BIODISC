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
"""Tests for the dataset preflight decision contract.

preflight_dataset itself needs a real download (integration); these test the
PreflightResult pass/fail contract that the CLI relies on.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline.dataset_preflight import PreflightResult  # noqa: E402


def test_passes_iff_no_issues():
    r = PreflightResult(dataset_id="X")
    r.passes = not r.issues
    assert r.passes is True
    r.issues = ["download_failed: timeout"]
    r.passes = not r.issues
    assert r.passes is False


def test_as_dict_roundtrips():
    r = PreflightResult(dataset_id="G", n_samples=10, n_groups=2,
                        group_sizes={"0": 5, "1": 5}, n_significant=12)
    d = r.as_dict()
    assert d["dataset_id"] == "G"
    assert d["group_sizes"] == {"0": 5, "1": 5}
    assert d["n_significant"] == 12


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
