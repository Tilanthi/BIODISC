"""Gene symbol resolver for probe IDs."""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GeneResolutionResult:
    """Result of probe ID to gene symbol resolution."""

    success: bool
    original_identifiers: List[str]
    resolved_genes: List[str]
    unmapped_probes: List[str]
    mapping_rate: float
    warning_message: Optional[str]

class GeneResolver:
    """Resolve probe IDs to gene symbols."""

    def __init__(self):
        self.resolution_attempts = 0
        self.resolution_successes = 0
        self.resolution_failures = 0

        # MINIMUM mapping rate to accept results
        self.MIN_MAPPING_RATE = 0.8  # 80% of probes must map

        logger.info("🧬 GeneResolver initialized")
        logger.info(f"   Minimum mapping rate: {self.MIN_MAPPING_RATE*100:.0f}%")

    def resolve_probes_to_genes(
        self,
        identifiers: List[str],
        platform_id: Optional[str] = None
    ) -> GeneResolutionResult:
        """
        Resolve probe IDs to gene symbols.

        Args:
            identifiers: List of probe IDs or gene symbols
            platform_id: Optional platform ID for better resolution

        Returns:
            GeneResolutionResult with resolution status
        """

        self.resolution_attempts += 1

        logger.info(f"🔬 Resolving {len(identifiers)} identifiers to gene symbols")

        # Check if already gene symbols
        from .platform_parser import PlatformParser
        parser = PlatformParser()
        has_probes, probe_fraction = parser.detect_probe_ids(identifiers)

        if not has_probes:
            # Already gene symbols - return as-is
            logger.info("✅ Identifiers are already gene symbols (no resolution needed)")
            self.resolution_successes += 1
            return GeneResolutionResult(
                success=True,
                original_identifiers=identifiers,
                resolved_genes=identifiers,
                unmapped_probes=[],
                mapping_rate=1.0,
                warning_message=None
            )

        # CRITICAL: Probe IDs detected - need to resolve
        logger.warning(f"⚠️  PROBE IDS DETECTED: {probe_fraction:.1%} are probe IDs")
        logger.warning(f"   Sample probes: {identifiers[:5]}")

        # Try to resolve (simplified for implementation)
        resolved_genes = []
        unmapped_probes = []

        for probe_id in identifiers:
            if parser.is_probe_id(probe_id):
                # In real implementation, would query platform annotation
                # For now, mark as unmapped
                unmapped_probes.append(probe_id)
                resolved_genes.append(f"UNKNOWN_GENE_{probe_id}")
            else:
                # Already a gene symbol
                resolved_genes.append(probe_id)

        mapping_rate = (len(resolved_genes) - len(unmapped_probes)) / len(identifiers)

        # Check if resolution failed
        if len(unmapped_probes) > 0:
            self.resolution_failures += 1

            warning_msg = (
                f"FAILED to resolve {len(unmapped_probes)} probe IDs to gene symbols. "
                f"Gene symbols are required for biological interpretation. "
                f"Unmapped probes: {unmapped_probes[:10]}"
            )

            logger.error(f"❌ {warning_msg}")

            return GeneResolutionResult(
                success=False,
                original_identifiers=identifiers,
                resolved_genes=resolved_genes,
                unmapped_probes=unmapped_probes,
                mapping_rate=mapping_rate,
                warning_message=warning_msg
            )

        # Success
        self.resolution_successes += 1
        logger.info(f"✅ All {len(identifiers)} identifiers resolved to gene symbols")

        return GeneResolutionResult(
            success=True,
            original_identifiers=identifiers,
            resolved_genes=resolved_genes,
            unmapped_probes=[],
            mapping_rate=1.0,
            warning_message=None
        )

    def get_statistics(self) -> Dict:
        """Get resolution statistics."""
        return {
            'resolution_attempts': self.resolution_attempts,
            'resolution_successes': self.resolution_successes,
            'resolution_failures': self.resolution_failures,
            'success_rate': f"{(self.resolution_successes / max(self.resolution_attempts, 1)) * 100:.2f}%"
        }
