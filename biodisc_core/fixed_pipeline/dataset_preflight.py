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
"""Pre-flight a candidate GEO dataset through the full discovery pipeline gates.

Phase 3's enabler. Expanding the verified dataset pool (the structural throughput +
replication ceiling) can't be done by guessing GSE IDs — a dataset must actually
download, map probes to gene symbols, expose a binary case/control design, and yield
differential signal. This runs all four checks on a candidate and reports exactly
what passes or fails, so datasets can be added to ``real_datasets.py`` only when they
genuinely clear the gates.

Usage:
    python -m biodisc_core.fixed_pipeline.dataset_preflight GSE2034
    python -m biodisc_core.fixed_pipeline.dataset_preflight --add GSE2034 "title" "question"

Never silently adds a dataset: ``--add`` appends to REAL_GEO_DATASETS only after a
passing preflight, and the append is logged.
"""
from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

MIN_VALID_GENES = 100
MIN_SIG_GENES = 3
MIN_GROUP_SIZE = 3


@dataclass
class PreflightResult:
    dataset_id: str
    passes: bool = False
    download_ok: bool = False
    n_samples: int = 0
    n_groups: int = 0
    group_sizes: dict = field(default_factory=dict)
    n_genes: int = 0
    n_valid_genes: int = 0
    n_significant: int = 0
    de_ok: bool = False
    issues: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {k: (v if not isinstance(v, dict) else dict(v))
                for k, v in self.__dict__.items()}


def preflight_dataset(geo_id: str, n_genes: int = 2000) -> PreflightResult:
    """Run a candidate dataset through download -> gene mapping -> groups -> DE."""
    res = PreflightResult(dataset_id=geo_id)

    # 1. Download (reuses the orchestrator's real-data path).
    try:
        from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import (
            create_fixed_discovery_orchestrator)
        orch = create_fixed_discovery_orchestrator()
        expr, genes, labels = orch.download_real_data_multi_repo(
            geo_id, "GEO", n_samples=12, n_genes=n_genes)
    except Exception as e:  # noqa: BLE001
        res.issues.append(f"download_failed: {type(e).__name__}: {e}")
        return res
    res.download_ok = True

    # 2. Binary case/control design.
    groups = Counter(list(labels))
    res.n_samples = len(labels)
    res.n_groups = len(groups)
    res.group_sizes = {str(k): int(v) for k, v in groups.items()}
    if res.n_groups < 2:
        res.issues.append(f"not_binary_design ({res.n_groups} group(s))")
    elif any(v < MIN_GROUP_SIZE for v in groups.values()):
        res.issues.append(f"group_too_small (sizes {res.group_sizes}; need >={MIN_GROUP_SIZE} each)")

    # 3. Probe -> gene-symbol mapping (HGNC validation).
    try:
        from biodisc_core.fixed_pipeline.gene_symbol_validation import (
            create_gene_symbol_validator, ValidationResult)
        validator = create_gene_symbol_validator()
        val_results, _ = validator.validate_gene_symbols(gene_symbols=genes, reject_on_invalid=False)
        n_valid = sum(1 for r in val_results if getattr(r, "result", None) == ValidationResult.VALID)
    except Exception as e:  # noqa: BLE001
        n_valid = 0
        res.issues.append(f"gene_validation_failed: {type(e).__name__}: {e}")
    res.n_genes = len(genes)
    res.n_valid_genes = n_valid
    if n_valid < MIN_VALID_GENES:
        res.issues.append(f"gene_mapping_poor ({n_valid}/{res.n_genes} valid; need >={MIN_VALID_GENES})")

    # 4. Differential signal.
    try:
        from biodisc_core.fixed_pipeline.differential_expression import (
            create_differential_expression_analyzer)
        de = create_differential_expression_analyzer().perform_differential_expression_analysis(
            expr, genes, labels, "preflight", geo_id)
        res.de_ok = True
        res.n_significant = de.significant_genes
        if de.significant_genes < MIN_SIG_GENES:
            res.issues.append(f"low_significance ({de.significant_genes} sig genes; need >={MIN_SIG_GENES})")
    except Exception as e:  # noqa: BLE001
        res.issues.append(f"de_failed: {type(e).__name__}: {e}")

    res.passes = not res.issues
    return res


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Pre-flight a candidate GEO dataset through the pipeline gates.")
    p.add_argument("geo_id")
    p.add_argument("--add", nargs=2, metavar=("TITLE", "QUESTION"), default=None,
                   help="if preflight passes, append to REAL_GEO_DATASETS with this title+question")
    args = p.parse_args(argv)

    res = preflight_dataset(args.geo_id)
    print(json.dumps(res.as_dict(), indent=2))
    if not res.passes:
        print(f"\n❌ {args.geo_id} FAILS preflight — not added.")
        return 1
    print(f"\n✅ {args.geo_id} PASSES preflight.")
    if args.add:
        import json as _json
        from pathlib import Path as _Path
        from biodisc_core.fixed_pipeline import real_datasets as _rd
        title, question = args.add
        sidecar = _Path(_rd.__file__).parent / "real_datasets_extra.json"
        extras = []
        if sidecar.exists():
            try:
                extras = _json.loads(sidecar.read_text())
            except Exception:
                extras = []
        extras = [e for e in extras if e.get("id") != args.geo_id]  # dedupe by id
        extras.append({
            "id": args.geo_id, "repo": "GEO", "title": title,
            "organism": "Homo sapiens", "samples": res.n_samples,
            "data_type": "gene_expression", "question": question,
            "url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={args.geo_id}",
        })
        sidecar.write_text(_json.dumps(extras, indent=2))
        logger.info("persisted %s to real_datasets_extra.json (preflight passed)", args.geo_id)
        print(f"➕ persisted {args.geo_id} to real_datasets_extra.json "
              f"(restart the loop to use it; survives restart).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
