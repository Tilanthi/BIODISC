"""Discovery cache for duplicate detection."""
from collections import OrderedDict
from typing import Dict, Set, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DiscoveryCache:
    """LRU cache for tracking discoveries and detecting duplicates."""

    def __init__(self, max_size: int = 10000):
        """
        Initialize discovery cache.

        Args:
            max_size: Maximum number of discovery fingerprints to track
        """
        self.max_size = max_size
        self.discoveries: OrderedDict[str, Dict] = OrderedDict()
        self.question_dataset_pairs: Set[str] = set()
        self.statistical_profiles: Set[str] = set()

        # Statistics
        self.total_discoveries = 0
        self.duplicates_detected = 0

        logger.info(f"💾 DiscoveryCache initialized (max_size={max_size})")

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

        # Not a duplicate
        return False, ""

    def add_discovery(self, fingerprint: 'DiscoveryFingerprint', discovery: Dict):
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
