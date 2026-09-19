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
"""Admission protocol for acquired scientific methods (V9.1).

An acquired method is a scientific analysis capability bound to peer-reviewed
source code (e.g. WGCNA from its repo + paper), as opposed to an invented
heuristic. Paper2Agent's protocol for converting code into usable tools:
run the SOURCE first with traceable inputs, pin its native outputs as the
reference baseline, and require the wrapped tool to agree — plus fresh-verifier
testing. Their measured conversion rate (74/100 papers) is the reason this
registry QUARANTINES by default: an unverified acquired method must never mint
discoveries, exactly as an unreplicated candidate never reaches the genuine
store.

Admission requirements (all must carry evidence):
  * reference_agreement — the wrapped tool reproduces the source repo's outputs
    on traceable inputs (the Paper2Agent core check).
  * store_fpr_check — the method demonstrates its false-positive behavior on
    the discovery store's controls (a new analysis vocabulary is a new way to
    generate false positives).
  * human_review — a human accepted the method (propose-only discipline,
    mirroring the RSI miner).
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

from ..paths import DATA_ROOT

PROJECT_ROOT = DATA_ROOT
REGISTRY_FILE = PROJECT_ROOT / "acquired_methods.json"

ADMISSION_REQUIREMENTS = ("reference_agreement", "store_fpr_check", "human_review")

STATE_QUARANTINED = "quarantined"
STATE_ADMITTED = "admitted"
STATE_REJECTED = "rejected"


@dataclass
class AcquiredMethod:
    """A scientific method acquired from peer-reviewed source, under admission."""
    method_id: str
    name: str
    source_repo: str
    source_commit: str
    source_paper: str
    tools: List[str]
    state: str = STATE_QUARANTINED
    evidence: dict = field(default_factory=lambda: {
        "reference_agreement": False, "store_fpr_check": False, "human_review": False})


def evaluate_admission(m: AcquiredMethod) -> dict:
    """Decide a method's admission state from its recorded evidence.

    admitted only when every requirement carries evidence; rejected only by an
    explicit human reject (never for missing evidence — that stays quarantined,
    the honest state for "not yet verified").
    """
    if m.state == STATE_REJECTED:
        return {"state": STATE_REJECTED, "unmet": []}
    unmet = [r for r in ADMISSION_REQUIREMENTS if not m.evidence.get(r)]
    if unmet:
        return {"state": STATE_QUARANTINED, "unmet": unmet}
    return {"state": STATE_ADMITTED, "unmet": []}


def is_admitted(method_id: str, path: Optional[Path] = None,
                methods: Optional[List[AcquiredMethod]] = None) -> bool:
    """THE gate the pipeline must consult before an acquired method mints anything."""
    if methods is None:
        methods = load_registry(path)
    for m in methods:
        if m.method_id == method_id:
            return evaluate_admission(m)["state"] == STATE_ADMITTED
    return False  # unregistered = never admitted


def load_registry(path: Optional[Path] = None) -> List[AcquiredMethod]:
    p = Path(path) if path is not None else REGISTRY_FILE
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return [AcquiredMethod(**m) for m in data.get("methods", [])]


def save_registry(methods: List[AcquiredMethod], path: Optional[Path] = None) -> None:
    p = Path(path) if path is not None else REGISTRY_FILE
    doc = {
        "schema": "biodisc-acquired-methods/1.0",
        "note": ("quarantined until reference_agreement + store_fpr_check + "
                 "human_review all carry evidence; the pipeline consults "
                 "is_admitted() before any acquired method mints discoveries"),
        "methods": [asdict(m) for m in methods],
    }
    p.write_text(json.dumps(doc, indent=2))
    logger.info("acquired-methods registry -> %s (%d methods)", p, len(methods))


__all__ = ["AcquiredMethod", "evaluate_admission", "is_admitted",
           "load_registry", "save_registry", "ADMISSION_REQUIREMENTS",
           "REGISTRY_FILE"]
