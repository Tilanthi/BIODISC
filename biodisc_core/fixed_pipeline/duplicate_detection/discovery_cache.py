"""Discovery cache for duplicate detection."""
import json
import os
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, Set, Optional, Tuple, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

NEAR_DUP_OVERLAP = 0.7

_DEFAULT_REGISTRY = Path(__file__).resolve().parents[3] / "duplicate_registry.json"


def _registry_file():
    """Registry path, honoring the BIODISC_DUPLICATE_REGISTRY override (call-time,
    not import-time, so per-test conftest isolation works)."""
    env = os.environ.get("BIODISC_DUPLICATE_REGISTRY")
    return Path(env) if env else _DEFAULT_REGISTRY


class DiscoveryCache:
    """LRU cache for tracking discoveries and detecting duplicates."""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.discoveries: OrderedDict[str, Dict] = OrderedDict()
        self.question_dataset_pairs: Set[str] = set()
        self.statistical_profiles: Set[str] = set()
        self.dataset_gene_sets: Dict[str, List[List[str]]] = defaultdict(list)

        self.total_discoveries = 0
        self.duplicates_detected = 0

        # Load the persisted gene-set registry so dedup works across restarts.
        self._load_registry()

        logger.info(f"💾 DiscoveryCache initialized (max_size={max_size}, "
                    f"registry: {sum(len(v) for v in self.dataset_gene_sets.values())} gene-sets)")

    def _load_registry(self):
        try:
            rf = _registry_file()
            if rf.exists():
                data = json.loads(rf.read_text())
                self.dataset_gene_sets = defaultdict(list, {k: v for k, v in data.items()})
                logger.info(f"📂 Loaded {sum(len(v) for v in self.dataset_gene_sets.values())} "
                            f"gene-sets from {rf.name}")
        except Exception as e:
            logger.warning(f"Could not load duplicate registry (non-fatal): {e}")

    def _save_registry(self):
        try:
            _registry_file().write_text(json.dumps(dict(self.dataset_gene_sets)))
        except Exception as e:
            logger.warning(f"Could not save duplicate registry (non-fatal): {e}")

    def is_duplicate(self, fingerprint: 'DiscoveryFingerprint') -> Tuple[bool, str]:
        """
        Check if discovery is a duplicate.

        Returns:
            (is_duplicate, reason)
        """

        # Check 1: Exact same combined hash
        if fingerprint.combined_hash in self.discoveries:
            self.duplicates_detected += 1
            existing = self.discoveries[fingerprint.combined_hash]
            reason = f"Exact duplicate (seen {existing['count']} times, first: {existing['first_seen']})"
            logger.warning(f"🚫 DUPLICATE: {reason}")
            return True, reason

        # Check 2: Same question + dataset (even if stats differ slightly)
        qd_pair = f"{fingerprint.question_hash}_{fingerprint.dataset_hash}"
        if qd_pair in self.question_dataset_pairs:
            self.duplicates_detected += 1
            reason = f"Same question+dataset pair (duplicate analysis)"
            logger.warning(f"🚫 DUPLICATE: {reason}")
            return True, reason

        # Check 3: Same statistical profile (suspicious - indicates template)
        if fingerprint.statistical_hash in self.statistical_profiles:
            self.duplicates_detected += 1
            reason = f"Identical statistical profile (template pattern)"
            logger.warning(f"🚫 DUPLICATE: {reason}")
            return True, reason

        # Check 4: Near-duplicate by top-DE-gene overlap on the SAME dataset.
        # Different question phrasings of the same contrast (e.g. "lipid-metabolism
        # genes in mouse liver" vs "high-fat diet hepatic expression" on GSE15822)
        # share most of their top genes -> the same finding re-derived.
        if fingerprint.top_genes and fingerprint.dataset_id:
            new_set = set(fingerprint.top_genes)
            for stored in self.dataset_gene_sets.get(fingerprint.dataset_id, []):
                stored_set = set(stored)
                if not stored_set:
                    continue
                overlap = len(new_set & stored_set) / min(len(new_set), len(stored_set))
                if overlap >= NEAR_DUP_OVERLAP:
                    self.duplicates_detected += 1
                    reason = (f"Near-duplicate: {int(overlap * 100)}% top-gene overlap "
                              f"with an existing discovery on {fingerprint.dataset_id} "
                              f"(same contrast re-derived)")
                    logger.warning(f"🚫 DUPLICATE: {reason}")
                    return True, reason

        # Not a duplicate
        return False, ""

    def add_discovery(self, fingerprint: 'DiscoveryFingerprint', discovery: Dict[str, Any]):
        """Add discovery to cache."""

        # LRU eviction if at capacity
        if len(self.discoveries) >= self.max_size:
            oldest = next(iter(self.discoveries))
            del self.discoveries[oldest]
            logger.debug(f"Evicted oldest discovery: {oldest[:12]}...")

        # Add to cache
        now = datetime.now().isoformat()

        # Update existing or add new
        if fingerprint.combined_hash in self.discoveries:
            self.discoveries[fingerprint.combined_hash]['count'] += 1
            self.discoveries[fingerprint.combined_hash]['last_seen'] = now
        else:
            self.discoveries[fingerprint.combined_hash] = {
                'count': 1,
                'first_seen': now,
                'last_seen': now,
                'fingerprint': fingerprint
            }
            self.total_discoveries += 1

        # Track question+dataset pairs
        qd_pair = f"{fingerprint.question_hash}_{fingerprint.dataset_hash}"
        self.question_dataset_pairs.add(qd_pair)

        # Track statistical profiles
        self.statistical_profiles.add(fingerprint.statistical_hash)

        # Track top-gene sets per dataset (for same-dataset overlap dedup)
        if fingerprint.top_genes and fingerprint.dataset_id:
            self.dataset_gene_sets[fingerprint.dataset_id].append(list(fingerprint.top_genes))
            self._save_registry()  # persist so dedup survives restarts

        logger.info(f"✅ Discovery added to cache (total: {self.total_discoveries}, duplicates: {self.duplicates_detected})")

    def get_statistics(self) -> Dict:
        """Get cache statistics."""
        return {
            'total_discoveries': self.total_discoveries,
            'duplicates_detected': self.duplicates_detected,
            'duplicate_rate': f"{(self.duplicates_detected / max(self.total_discoveries, 1)) * 100:.2f}%",
            'cache_size': len(self.discoveries),
            'unique_qd_pairs': len(self.question_dataset_pairs)
        }
