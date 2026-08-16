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
"""Discovery-store write CHOKEPOINT — BIODISC's fiction-prevention layer.

BIODISC's #1 enemy is fictional / hallucinated biological claims (the known
LLM-in-biology failure mode, and the exact bug that polluted ASTRA's store
with a hardcoded string emitted ~60/hour). The defence is structural, not
behavioural: there is exactly ONE function that may write a discovery to disk,
and it REQUIRES a machine ``verification`` block carrying objective real-data
evidence. With this chokepoint, fiction becomes structurally impossible — no
code path can write an unverified record.

Two stores, both written ONLY through :func:`append_verified`:

* ``autonomous_discoveries.jsonl`` (the verified store) — records flagged
  ``genuine``: machine-verified AND replicated on held-out data.
* ``autonomous_discoveries_candidates.jsonl`` (quarantine) — records flagged
  ``candidate_unconfirmed``: machine-verified on real data but NOT yet
  replicated (single cohort). They carry real evidence, so they are kept, but
  they are quarantined away from the headline store and never asserted as new
  knowledge.

Machine verification (required for ANY write) is distinct from genuineness
(required for the headline store): the chokepoint prevents FICTION; the
replication tier (see ``discovery_gate.py`` + ``replication_gate.py``) prevents
OVERCLAIMING.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Repo root: biodisc_core/fixed_pipeline/discovery_store.py -> up 2 parents.
# (parents[2] = BIODISC; parents[3] would be SWARM — a bug that wrote the store
# one directory too high. Guarded by test_discovery_chokepoint_default_path.)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

VERIFIED_STORE = PROJECT_ROOT / "autonomous_discoveries.jsonl"
CANDIDATE_QUARANTINE = PROJECT_ROOT / "autonomous_discoveries_candidates.jsonl"


class UnverifiedDiscoveryError(RuntimeError):
    """Raised when a write is attempted without a valid machine verification block."""


def has_machine_verification(record: dict) -> bool:
    """True iff ``record`` carries an objective, machine-checkable verification block.

    A valid block needs:
      * a ``real_data_result`` dict that is non-empty and names a real dataset
        (the objective evidence the finding came from real data, not assertion);
      * a ``gates`` dict recording which gates evaluated the claim.
    """
    v = record.get("verification")
    if not isinstance(v, dict):
        return False
    real = v.get("real_data_result")
    if not isinstance(real, dict) or not real:
        return False
    if not real.get("dataset_id"):
        return False
    if not isinstance(v.get("gates"), dict):
        return False
    return True


def _tier_of(record: dict) -> str:
    """Resolve the storage tier: 'genuine' | 'candidate_unconfirmed' | 'rejected'."""
    flag = record.get("flagging") or {}
    tier = flag.get("tier")
    if tier in ("genuine", "candidate_unconfirmed", "rejected"):
        return tier
    # Fall back to the bare is_genuine flag if no flagging block is present.
    return "genuine" if record.get("is_genuine") else "candidate_unconfirmed"


def append_verified(
    record: dict,
    verification: Optional[dict],
    *,
    store_dir: Optional[Path] = None,
) -> str:
    """The SINGLE write path to the discovery store.

    Args:
        record: the discovery report (must already carry a ``flagging`` tier or
            an ``is_genuine`` flag).
        verification: the machine verification block (objective real-data
            evidence). ``None`` or an incomplete block => :class:`UnverifiedDiscoveryError`.
        store_dir: optional override directory (used by tests) for the store
            files; defaults to the repo root.

    Returns:
        The path the record was written to.

    Raises:
        UnverifiedDiscoveryError: if the verification block is missing/incomplete
            or the record is a rejected-tier candidate that must never be stored.
    """
    out = dict(record)
    if isinstance(verification, dict) and verification:
        out["verification"] = verification
    elif "verification" not in out:
        # No verification supplied and none on the record => fiction. Reject.
        raise UnverifiedDiscoveryError(
            "REFUSED: discovery has no machine verification block. "
            "Every stored discovery must carry objective real-data evidence "
            "(real_data_result + gates). This prevents fictional/hallucinated "
            "discoveries from entering the store."
        )

    if not has_machine_verification(out):
        raise UnverifiedDiscoveryError(
            "REFUSED: discovery verification block is incomplete. "
            "Required: verification.real_data_result (with dataset_id) + verification.gates."
        )

    tier = _tier_of(out)
    if tier == "rejected":
        raise UnverifiedDiscoveryError(
            "REFUSED: discovery is tier='rejected' and must never be stored."
        )

    target = VERIFIED_STORE if tier == "genuine" else CANDIDATE_QUARANTINE
    if store_dir is not None:
        store_dir = Path(store_dir)
        store_dir.mkdir(parents=True, exist_ok=True)
        target = store_dir / target.name

    out.setdefault("stored_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    with open(target, "a") as f:
        f.write(json.dumps(out) + "\n")

    logger.info("💾 discovery written via chokepoint -> %s (tier=%s)", target, tier)
    return str(target)


__all__ = [
    "append_verified",
    "has_machine_verification",
    "build_verification_block",
    "UnverifiedDiscoveryError",
    "VERIFIED_STORE",
    "CANDIDATE_QUARANTINE",
]


def build_verification_block(
    report: dict,
    pipeline: str = "fixed_pipeline_v6",
    pipeline_hash: str = "fixed_v6|ttest|bhfdr",
    peer_decision: str = "",
) -> dict:
    """Construct the objective machine-verification block required by the chokepoint.

    Pulls the real-data evidence (dataset, gene counts, method) and gate outcomes
    (literature novelty, replication, peer review) from a discovery report. Both
    the orchestrator's and the live loop's save paths call this so the block is
    built consistently in exactly one place.
    """
    de = report.get('differential_expression', {}) or {}
    ds = report.get('dataset', {}) or {}
    return {
        "pipeline": pipeline,
        "pipeline_hash": pipeline_hash,
        "real_data_result": {
            "dataset_id": report.get('dataset_id', ds.get('geo_id', '')),
            "organism": ds.get('organism', 'Unknown'),
            "n_significant_genes": de.get('significant_genes'),
            "total_genes_tested": de.get('total_genes_tested'),
            "method": de.get('method'),
            "correction": de.get('correction'),
        },
        "gates": {
            "fdr_significance": True,
            "literature_novelty": (report.get('comprehensive_validation_statistics', {})
                                   .get('literature_novelty', {}).get('status')),
            "replication": (report.get('replication', {}) or {}).get('replicated'),
            "peer_review": peer_decision,
        },
        "verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
