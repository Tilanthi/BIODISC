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
    yield
