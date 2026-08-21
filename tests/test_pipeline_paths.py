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
"""Guard tests for the pipeline's central data root (fixed_pipeline/paths.py).

The data root replaced seven per-file ``PROJECT_ROOT =
Path(__file__).resolve().parents[2]`` definitions. Two invariants:

1. the DEFAULT is byte-for-byte the historical repo root — the always-on
   watchdog loop's stores must not move (this is the guard
   discovery_store.py's comment always promised);
2. ``BIODISC_DATA_ROOT`` relocates every pipeline path consistently.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from biodisc_core.fixed_pipeline import paths  # noqa: E402
from biodisc_core.fixed_pipeline import (  # noqa: E402
    capability_index,
    discovery_status,
    discovery_store,
    rsi_miner,
    verdict_log,
)


def test_default_data_root_is_repo_root():
    """Without BIODISC_DATA_ROOT the data root must be the BIODISC repo root
    (parents[2] of the package) — never SWARM (parents[3], the old bug)."""
    assert paths.DATA_ROOT == Path(__file__).resolve().parents[1]
    assert paths.DATA_ROOT.name == "BIODISC"


def test_all_pipeline_paths_share_the_central_root():
    """Every module-level path derives from the same DATA_ROOT."""
    root = paths.DATA_ROOT
    assert discovery_store.VERIFIED_STORE == root / "autonomous_discoveries.jsonl"
    assert discovery_store.CANDIDATE_QUARANTINE == root / "autonomous_discoveries_candidates.jsonl"
    assert verdict_log.VERDICT_LOG == root / "discovery_verdicts.jsonl"
    assert capability_index.INDEX_FILE == root / "capability_index.json"
    assert capability_index.GENUINE_STORE == root / "autonomous_discoveries.jsonl"
    assert discovery_status.STATUS_FILE == root / "discovery_status.json"
    assert rsi_miner.PROPOSALS_MD == root / "rsi_proposals.md"


def test_biodisc_data_root_env_relocates_pipeline(tmp_path):
    """A subprocess with BIODISC_DATA_ROOT set must resolve every store under
    the override — import-time env reading, hence the subprocess."""
    script = (
        "from biodisc_core.fixed_pipeline import paths, discovery_store, verdict_log; "
        "import json; "
        "print(json.dumps({'data_root': str(paths.DATA_ROOT), "
        "'verified': str(discovery_store.VERIFIED_STORE), "
        "'verdict': str(verdict_log.VERDICT_LOG)}))"
    )
    env = dict(os.environ, BIODISC_DATA_ROOT=str(tmp_path))
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    out = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, env=env, check=True
    )
    resolved = json.loads(out.stdout.strip().splitlines()[-1])
    assert resolved["data_root"] == str(tmp_path)
    assert resolved["verified"] == str(tmp_path / "autonomous_discoveries.jsonl")
    assert resolved["verdict"] == str(tmp_path / "discovery_verdicts.jsonl")
