"""Microarray platform parser for probe ID to gene symbol mapping."""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class PlatformAnnotation:
    """Microarray platform annotation."""

    platform_id: str
    platform_name: str
    organism: str
    probe_count: int
    probe_to_gene: Dict[str, str]  # probe_id -> gene_symbol
    annotation_source: str

class PlatformParser:
    """Parse microarray platform annotations and map probe IDs to genes."""

    def __init__(self):
        self.platform_cache: Dict[str, PlatformAnnotation] = {}
        self.parse_attempts = 0
        self.parse_successes = 0

        logger.info("🧬 PlatformParser initialized for probe-to-gene mapping")

    def is_probe_id(self, identifier: str) -> bool:
        """
        Check if identifier is a probe ID (numeric) or gene symbol.

        Probe IDs are typically numeric (e.g., '455', '1195', '382').
        Gene symbols are alphanumeric with letters (e.g., 'BRCA1', 'TP53').
        """

        # Check if purely numeric (probe ID)
        if identifier.isdigit():
            return True

        # Check if probe ID pattern (affymetrix-style: 12345_at, 455_s_at)
        if re.match(r'^\d+_(s_)?at$', identifier):
            return True

        # Check if Illumina probe ID (e.g., ILMN_12345)
        if re.match(r'^ILMN_\d+$', identifier):
            return True

        # Otherwise likely a gene symbol
        return False

    def detect_probe_ids(self, gene_list: List[str]) -> tuple[bool, float]:
        """
        Detect if gene list contains probe IDs instead of gene symbols.

        Returns:
            (has_probe_ids, probe_fraction)
        """

        if not gene_list:
            return False, 0.0

        probe_count = sum(1 for gene in gene_list if self.is_probe_id(gene))
        probe_fraction = probe_count / len(gene_list)

        # If >50% are probe IDs, consider it probe ID list
        has_probes = probe_fraction > 0.5

        logger.info(f"🔍 Gene list analysis: {probe_count}/{len(gene_list)} probe IDs ({probe_fraction:.1%})")

        return has_probes, probe_fraction

    def parse_platform_from_geo(self, platform_id: str) -> Optional[PlatformAnnotation]:
        """
        Parse platform annotation from GEO.

        This is a simplified version - real implementation would query GEO
        for platform annotation files (.annot).

        Args:
            platform_id: GEO platform ID (e.g., 'GPL570')

        Returns:
            PlatformAnnotation if successful, None otherwise
        """

        self.parse_attempts += 1

        logger.info(f"📡 Parsing platform: {platform_id}")

        # SIMPLIFIED: For implementation, create mock annotation
        # Real implementation would download and parse .annot file from GEO

        # Common platforms
        known_platforms = {
            'GPL570': {  # Affymetrix Human Genome U133 Plus 2.0 Array
                'name': 'Affymetrix Human Genome U133 Plus 2.0 Array',
                'organism': 'Homo sapiens',
                'probe_count': 54675
            },
            'GPL96': {  # Affymetrix Human Genome U133A Array
                'name': 'Affymetrix Human Genome U133A Array',
                'organism': 'Homo sapiens',
                'probe_count': 22283
            },
            'GPL97': {  # Affymetrix Human Genome U133B Array
                'name': 'Affymetrix Human Genome U133B Array',
                'organism': 'Homo sapiens',
                'probe_count': 22326
            }
        }

        if platform_id not in known_platforms:
            logger.warning(f"Unknown platform: {platform_id}")
            return None

        info = known_platforms[platform_id]

        annotation = PlatformAnnotation(
            platform_id=platform_id,
            platform_name=info['name'],
            organism=info['organism'],
            probe_count=info['probe_count'],
            probe_to_gene={},  # Would be populated from .annot file
            annotation_source='mock'
        )

        self.platform_cache[platform_id] = annotation
        self.parse_successes += 1

        logger.info(f"✅ Platform parsed: {info['name']} ({info['probe_count']} probes)")

        return annotation

    def get_platform_annotation(self, platform_id: str) -> Optional[PlatformAnnotation]:
        """Get cached platform annotation or parse if not cached."""

        if platform_id in self.platform_cache:
            return self.platform_cache[platform_id]

        return self.parse_platform_from_geo(platform_id)
