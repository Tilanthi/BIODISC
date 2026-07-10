"""Duplicate detection system."""
from typing import Dict, Tuple
from .discovery_fingerprint import DiscoveryFingerprint
from .discovery_cache import DiscoveryCache

class DuplicateDetector:
    """Duplicate detection system for discovery pipeline."""

    def __init__(self, max_cache_size: int = 10000):
        self.cache = DiscoveryCache(max_size=max_cache_size)
        self.rejections = 0

    def check_duplicate(self, discovery: Dict) -> Tuple[bool, str]:
        """
        Check if discovery is a duplicate.

        Args:
            discovery: Discovery report to check

        Returns:
            (is_duplicate, reason)
        """
        fingerprint = DiscoveryFingerprint.from_discovery(discovery)
        is_dup, reason = self.cache.is_duplicate(fingerprint)

        if is_dup:
            self.rejections += 1

        return is_dup, reason

    def register_discovery(self, discovery: Dict):
        """Register a non-duplicate discovery in the cache."""
        fingerprint = DiscoveryFingerprint.from_discovery(discovery)
        self.cache.add_discovery(fingerprint, discovery)

    def get_statistics(self) -> Dict:
        """Get detection statistics."""
        stats = self.cache.get_statistics()
        stats['rejections'] = self.rejections
        return stats

def create_duplicate_detector(max_cache_size: int = 10000):
    """Factory function to create duplicate detector."""
    return DuplicateDetector(max_cache_size=max_cache_size)
