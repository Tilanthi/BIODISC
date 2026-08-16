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
"""Shared pytest fixtures.

Isolates test-run verdicts from the production discovery_verdicts.jsonl: the
orchestrator's validate_discovery_comprehensive calls log_verdict
unconditionally, so without this every test that exercises validation would
pollute the production funnel/miner with synthetic verdicts (the apparent
"significance-failure" bottleneck turned out to be exactly this — synthetic
GSE11223/GSE99999 test data, not real discovery failures).
"""
import pytest


@pytest.fixture(autouse=True)
def _isolate_verdict_log(tmp_path, monkeypatch):
    monkeypatch.setenv("BIODISC_VERDICT_LOG", str(tmp_path / "test_verdicts.jsonl"))
    monkeypatch.setenv("BIODISC_DUPLICATE_REGISTRY", str(tmp_path / "test_dup_registry.json"))
    # Same reason, for the runtime status store the watchdog reads: the loop now
    # heartbeats from inside long operations, so any test that exercises
    # gene-symbol validation would otherwise rewrite the production
    # discovery_status.json — and that file is the watchdog's only evidence that
    # the loop is alive.
    monkeypatch.setenv("BIODISC_DISCOVERY_STATUS", str(tmp_path / "test_discovery_status.json"))
    # Likewise for the persisted HGNC verdict cache.
    monkeypatch.setenv("BIODISC_HGNC_CACHE", str(tmp_path / "test_hgnc_cache.json"))
    yield
