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
"""Control-case seeding and storage for the known-answer suite.

Cases are seeded ONLY from the genuine store (machine-verified + replicated
findings on real data). That is honest regression ground truth: the pipeline
already demonstrated these results once, so failing to recover them now means
the wiring broke. Hand-curated external expectations would require asserting
biology we have not verified ourselves — deliberately not done.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

from ..paths import DATA_ROOT

PROJECT_ROOT = DATA_ROOT
CASES_FILE = PROJECT_ROOT / "known_answer_cases.json"
GENUINE_STORE = PROJECT_ROOT / "autonomous_discoveries.jsonl"

MAX_GENES_PER_CASE = 5


@dataclass
class KnownAnswerCase:
    """One real finding the pipeline must be able to recover."""
    case_id: str
    dataset_id: str
    question: str
    genes: List[dict]            # [{symbol, direction (up|down), log2fc, fdr}]
    source: str = "genuine_store"
    discovery_id: str = ""
    seeded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


def _genes_from_record(rec: dict) -> List[dict]:
    de = rec.get("differential_expression") or {}
    pool = list(de.get("top_upregulated") or []) + list(de.get("top_downregulated") or [])
    genes = []
    for g in pool:
        sym = (g.get("gene_symbol") or "").upper().strip()
        if not sym:
            continue
        l2 = g.get("log2_fold_change")
        try:
            direction = g.get("regulation") or ("up" if float(l2) >= 0 else "down")
        except (TypeError, ValueError):
            direction = g.get("regulation") or "up"
        genes.append({"symbol": sym, "direction": direction,
                      "log2fc": l2, "fdr": g.get("fdr_p_value")})
    # strongest effects first, capped
    genes.sort(key=lambda g: abs(g.get("log2fc") or 0.0), reverse=True)
    return genes[:MAX_GENES_PER_CASE]


def seed_from_genuine_store(store_path: Optional[Path] = None,
                            max_cases: int = 10) -> List[KnownAnswerCase]:
    """Seed control cases from replicated genuine-tier records (most recent first)."""
    p = Path(store_path) if store_path is not None else GENUINE_STORE
    cases: List[KnownAnswerCase] = []
    seen_contrasts = set()
    if not p.exists():
        return cases
    lines = [l for l in p.read_text().splitlines() if l.strip()]
    for line in reversed(lines):
        if len(cases) >= max_cases:
            break
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        tier = (rec.get("flagging") or {}).get("tier")
        replicated = (rec.get("replication") or {}).get("replicated")
        if tier != "genuine" and not rec.get("is_genuine"):
            continue
        if not replicated:
            continue  # only replicated findings are "known answers"
        genes = _genes_from_record(rec)
        if not genes:
            continue
        # one control per distinct contrast: the store holds multiple genuine
        # discoveries from the same dataset with the same top genes — those
        # are the same control case, not more coverage.
        contrast_key = (rec.get("dataset_id") or (rec.get("dataset") or {}).get("geo_id") or "",
                        frozenset(g["symbol"] for g in genes))
        if contrast_key in seen_contrasts:
            continue
        seen_contrasts.add(contrast_key)
        ds = rec.get("dataset") or {}
        dataset_id = rec.get("dataset_id") or ds.get("geo_id") or ""
        if not dataset_id:
            continue
        cases.append(KnownAnswerCase(
            case_id=f"{dataset_id}:{rec.get('discovery_id', len(cases))}",
            dataset_id=dataset_id,
            question=(rec.get("question") or "")[:200],
            genes=genes,
            discovery_id=rec.get("discovery_id", "")))
    return cases


def save_cases(cases: List[KnownAnswerCase], path: Optional[Path] = None) -> None:
    p = Path(path) if path is not None else CASES_FILE
    p.write_text(json.dumps({"schema": "biodisc-known-answer-cases/1.0",
                             "cases": [asdict(c) for c in cases]}, indent=2))
    logger.info("seeded %d known-answer cases -> %s", len(cases), p)


def load_cases(path: Optional[Path] = None) -> List[KnownAnswerCase]:
    p = Path(path) if path is not None else CASES_FILE
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return [KnownAnswerCase(**c) for c in data.get("cases", [])]


__all__ = ["KnownAnswerCase", "seed_from_genuine_store", "save_cases", "load_cases",
           "CASES_FILE"]
