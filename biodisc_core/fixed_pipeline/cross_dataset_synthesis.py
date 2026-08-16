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
"""Cross-dataset module synthesis — find bridges BETWEEN datasets.

Single-dataset DE re-derives known biology: the obvious contrasts on public
datasets are already published. Cross-dataset synthesis looks for patterns
invisible to any one contrast:

* **Direction flips** — a gene UP in dataset A but DOWN in dataset B. A regulator
  that changes direction across contexts is a *bridge*: it can reframe both
  diseases, and it is the kind of unexpected cross-context pattern that does not
  fall out of a tumor-vs-normal list. Ranked by how many datasets it flips across.
* **Shared modules** — genes DE in many datasets with the SAME direction (a
  universal stress/cancer signature). Lower novelty, but worth measuring so the
  novelty gate can deprioritize ubiquitous genes.

These are where paradigm-shifting connections live, and — unlike tumor-vs-normal
— the space is genuinely under-mined.

First version (V8.0.23): operates on the top-DE gene lists already accumulated in
the genuine store. It produces bridge *hypotheses* for expert review; it does NOT
auto-stamp them as discoveries (the validation bar for a cross-dataset claim is
higher than for a single-dataset DE and is not automated here).

The anomaly-vs-expectation primitive (compare observed direction to a textbook-
direction baseline) is scaffolded as ``anomaly_vs_expectation``. The baseline is
a research item — a real "expected direction per gene x context" model is not
faked.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_STORE = _PROJECT_ROOT / "autonomous_discoveries.jsonl"


@dataclass
class BridgeCandidate:
    """A gene whose DE direction differs across datasets — a cross-context bridge."""
    gene: str
    direction_by_dataset: Dict[str, str]          # gse -> 'up' | 'down'
    up_in: List[str] = field(default_factory=list)
    down_in: List[str] = field(default_factory=list)
    flip_count: int = 0                            # number of dataset pairs that disagree
    datasets: int = 0

    @property
    def is_flip(self) -> bool:
        return bool(self.up_in) and bool(self.down_in)

    def as_dict(self) -> dict:
        return {
            "gene": self.gene, "is_flip": self.is_flip,
            "up_in": self.up_in, "down_in": self.down_in,
            "flip_count": self.flip_count, "datasets": self.datasets,
            "direction_by_dataset": self.direction_by_dataset,
        }


def _store_path(store_path: Optional[Path]) -> Path:
    return Path(store_path) if store_path else _DEFAULT_STORE


def load_gene_directions(store_path: Optional[Path] = None,
                         include_candidates: bool = False) -> Dict[str, Dict[str, str]]:
    """Return ``{gene_symbol: {gse: 'up'|'down'}}`` from the discovery store.

    Reads genuine discoveries by default (and candidate quarantine if requested).
    Direction comes from each DE result's top_upregulated / top_downregulated
    lists (with an explicit ``regulation`` field preferred when present).
    """
    path = _store_path(store_path)
    directions: Dict[str, Dict[str, str]] = defaultdict(dict)
    seen_pair = set()  # (gse, question) to avoid counting one contrast twice
    if not path.exists():
        return {}
    files = [path]
    if include_candidates:
        cand = path.parent / "autonomous_discoveries_candidates.jsonl"
        if cand.exists():
            files.append(cand)
    for f in files:
        with open(f) as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    d = json.loads(s)
                except Exception:
                    continue
                if not include_candidates and d.get("is_genuine") is not True:
                    continue
                ds = d.get("dataset") or {}
                gse = (d.get("dataset_id")
                       or (ds.get("geo_id") if isinstance(ds, dict) else "")
                       or (ds.get("gse_id") if isinstance(ds, dict) else "")
                       or "")
                if not gse:
                    continue
                key = (gse, d.get("question", ""))
                if key in seen_pair:          # one direction per (dataset, contrast)
                    continue
                seen_pair.add(key)
                de = d.get("differential_expression") or {}
                if not isinstance(de, dict):
                    continue
                for bucket, default in (("top_upregulated", "up"),
                                        ("top_downregulated", "down")):
                    for g in de.get(bucket) or []:
                        sym = g.get("gene_symbol") if isinstance(g, dict) else g
                        if not sym:
                            continue
                        direction = (g.get("regulation") if isinstance(g, dict) else None) or default
                        directions[sym].setdefault(gse, direction)  # first observation wins per gse
    return dict(directions)


def find_bridges(directions: Dict[str, Dict[str, str]],
                 min_datasets: int = 2) -> List[BridgeCandidate]:
    """Genes DE in >=min_datasets whose direction is NOT consistent across them.

    These are the cross-context bridges. Sorted by number of disagreeing dataset
    pairs (flip_count) descending, then by dataset count.
    """
    bridges: List[BridgeCandidate] = []
    for gene, per_ds in directions.items():
        if len(per_ds) < min_datasets:
            continue
        up_in = [gse for gse, d in per_ds.items() if d == "up"]
        down_in = [gse for gse, d in per_ds.items() if d == "down"]
        if not (up_in and down_in):
            continue  # consistent direction -> not a bridge (see find_shared instead)
        flip_count = len(up_in) * len(down_in)
        bridges.append(BridgeCandidate(
            gene=gene, direction_by_dataset=dict(per_ds),
            up_in=sorted(up_in), down_in=sorted(down_in),
            flip_count=flip_count, datasets=len(per_ds),
        ))
    bridges.sort(key=lambda b: (b.flip_count, b.datasets), reverse=True)
    return bridges


def find_shared(directions: Dict[str, Dict[str, str]],
                min_datasets: int = 3) -> List[Tuple[str, str, int, List[str]]]:
    """Genes DE in >=min_datasets with the SAME direction — a shared signature.

    Returns ``(gene, direction, dataset_count, [gses])`` sorted by prevalence.
    These are typically LOWER novelty (ubiquitous stress/housekeeping responses);
    the novelty gate should know about them so it can deprioritize.
    """
    shared = []
    for gene, per_ds in directions.items():
        if len(per_ds) < min_datasets:
            continue
        up = [g for g, d in per_ds.items() if d == "up"]
        down = [g for g, d in per_ds.items() if d == "down"]
        if up and not down:
            shared.append((gene, "up", len(up), sorted(up)))
        elif down and not up:
            shared.append((gene, "down", len(down), sorted(down)))
    shared.sort(key=lambda t: t[2], reverse=True)
    return shared


def anomaly_vs_expectation(observed: Dict[str, Dict[str, str]],
                           expected_baseline: Optional[Dict] = None):
    """Scaffold: surface genes whose observed direction CONTRADICTS a textbook
    expectation. A real baseline ("expected up/down per gene x context", mined
    from the literature or a curated database) is a research item and is NOT
    faked. With ``expected_baseline=None`` this returns an empty list and logs a
    notice so callers know the primitive is inert until a baseline is supplied.
    """
    if expected_baseline is None:
        logger.info("anomaly_vs_expectation: no baseline supplied -- primitive inert "
                    "(a textbook-direction baseline is a research item, not faked).")
        return []
    anomalies = []
    for gene, per_ds in observed.items():
        for ctx, direction in per_ds.items():
            expected = (expected_baseline.get(gene) or {}).get(ctx)
            if expected and expected != direction:
                anomalies.append({"gene": gene, "context": ctx,
                                   "observed": direction, "expected": expected})
    return anomalies


@dataclass
class CrossContextResult:
    """A gene's direction across multiple datasets/contexts (a queryable bridge check)."""
    gene: str
    directions: Dict[str, Optional[str]]      # context -> 'up' | 'down' | None
    up_in: List[str] = field(default_factory=list)
    down_in: List[str] = field(default_factory=list)
    flips: bool = False
    contexts_tested: int = 0
    note: str = ""

    def as_dict(self) -> dict:
        return {"gene": self.gene, "directions": self.directions, "up_in": self.up_in,
                "down_in": self.down_in, "flips": self.flips,
                "contexts_tested": self.contexts_tested, "note": self.note}


def evaluate_cross_context_direction(gene: str, contexts) -> CrossContextResult:
    """Test ``gene``'s direction across multiple contexts; flag a FLIP.

    ``contexts`` is an iterable of ``(expr, genes, labels, name)`` tuples. A gene
    that is UP in some contexts and DOWN in others is a cross-dataset BRIDGE —
    the paradigm-relevant pattern invisible to any single-dataset contrast (item 3
    of the rebuild). Reuses :func:`evaluate_gene_hypothesis` per context.
    """
    from biodisc_core.fixed_pipeline.gene_specific_hypothesis import evaluate_gene_hypothesis
    dirs: Dict[str, Optional[str]] = {}
    for ctx in contexts:
        expr, glist, labels, name = ctx
        r = evaluate_gene_hypothesis(expr, glist, labels, gene)
        dirs[name] = r.observed_direction if r.present else None
    up_in = sorted([k for k, v in dirs.items() if v == "up"])
    down_in = sorted([k for k, v in dirs.items() if v == "down"])
    flips = bool(up_in) and bool(down_in)
    return CrossContextResult(
        gene=gene, directions=dirs, up_in=up_in, down_in=down_in, flips=flips,
        contexts_tested=len(dirs),
        note=("cross-context FLIP (bridge candidate)" if flips
              else ("consistent direction" if (up_in or down_in) else "not measured")))


def check_gene_across_store(gene: str, store_path: Optional[Path] = None,
                            include_candidates: bool = False) -> CrossContextResult:
    """Queryable primitive: a gene's direction across all datasets in the genuine
    store (no new downloads). Flags flips = cross-dataset bridge candidates. This
    is the operational form of :func:`find_bridges` for a single gene of interest.
    """
    all_dirs = load_gene_directions(store_path, include_candidates)
    target = (gene or "").upper()
    per_ds: Dict[str, str] = {}
    for g, dsmap in all_dirs.items():
        if g.upper() == target:
            per_ds.update(dsmap or {})
    up_in = sorted([k for k, v in per_ds.items() if v == "up"])
    down_in = sorted([k for k, v in per_ds.items() if v == "down"])
    flips = bool(up_in) and bool(down_in)
    return CrossContextResult(
        gene=target, directions=per_ds, up_in=up_in, down_in=down_in, flips=flips,
        contexts_tested=len(per_ds),
        note=("cross-context FLIP (bridge candidate)" if flips
              else ("consistent direction" if (up_in or down_in) else "not measured in store")))


def summarize(store_path: Optional[Path] = None,
              include_candidates: bool = False,
              top: int = 15) -> dict:
    """Compute the cross-dataset synthesis and return a structured summary."""
    directions = load_gene_directions(store_path, include_candidates)
    bridges = find_bridges(directions)
    shared = find_shared(directions)
    n_genes = len(directions)
    n_datasets = len({gse for per_ds in directions.values() for gse in per_ds})
    summary = {
        "genes_with_direction": n_genes,
        "datasets_represented": n_datasets,
        "bridge_candidates": [b.as_dict() for b in bridges[:top]],
        "n_bridges_total": len(bridges),
        "shared_modules": [{"gene": g, "direction": d, "datasets": n, "in": gs}
                           for (g, d, n, gs) in shared[:top]],
        "n_shared_total": len(shared),
    }
    return summary


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Cross-dataset module synthesis: find bridges between datasets.")
    p.add_argument("--store", default=None, help="path to the discovery store jsonl")
    p.add_argument("--include-candidates", action="store_true")
    p.add_argument("--top", type=int, default=15)
    args = p.parse_args(argv)
    s = summarize(args.store, args.include_candidates, args.top)
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
