"""
V74 Data Source Validator - Validate Published Data Sources for Discoveries

CRITICAL PRINCIPLE: BIODISC genuine discoveries should be grounded in published data
from peer-reviewed sources, data repositories, archives, or other validated sources.

DATA SOURCE VALIDATION:
1. Peer-reviewed literature (journals, preprints)
2. Data repositories (GenBank, PDB, GEO, ArrayExpress, etc.)
3. Archives (institutional repositories, data archives)
4. Published datasets (supplementary materials, published databases)
5. Validated computational resources (curated databases, ontologies)

NOT ACCEPTABLE:
- Unverified claims without citations
- Personal anecdotes or unpublished observations
- Proprietary data without public validation
- Speculation without grounding in published evidence

Date: 2026-06-28
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import re
from datetime import datetime


class DataSourceType(Enum):
    """Types of acceptable data sources"""
    PEER_REVIEWED = "peer_reviewed"  # Peer-reviewed journals
    PREPRINT = "preprint"  # Preprint servers (bioRxiv, arXiv)
    DATA_REPOSITORY = "data_repository"  # Public data repositories (GenBank, PDB)
    INSTITUTIONAL_ARCHIVE = "institutional_archive"  # Institutional repositories
    PUBLISHED_DATASET = "published_dataset"  # Published datasets (supplementary materials)
    CURATED_DATABASE = "curated_database"  # Curated databases (GO, KEGG)
    VALIDATED_RESOURCE = "validated_resource"  # Community-validated resources


class DataQuality(Enum):
    """Quality levels of data sources"""
    HIGH = "high"  # Peer-reviewed, curated, extensively validated
    MEDIUM = "medium"  # Published but less curated
    LOW = "low"  # Publicly available but minimally validated
    UNVERIFIED = "unverified"  # Not validated - not acceptable for genuine discovery


@dataclass
class DataSource:
    """A data source used in a discovery"""
    source_type: DataSourceType
    identifier: str  # DOI, PMID, accession number, etc.
    quality: DataQuality
    description: str
    url: Optional[str] = None
    publication_date: Optional[datetime] = None
    authors: List[str] = field(default_factory=list)
    validated: bool = True  # Whether source has been validated


@dataclass
class DataSourceValidation:
    """Validation result for data sources in a discovery"""
    is_valid: bool
    confidence: float  # 0-1, confidence in validation
    sources_found: List[DataSource] = field(default_factory=list)
    missing_sources: List[str] = field(default_factory=list)
    quality_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Overall assessment
    data_quality_score: float = 0.0  # 0-1
    peer_reviewed_count: int = 0
    repository_count: int = 0
    unverified_count: int = 0


class DataSourceValidator:
    """
    Validate data sources for genuine discoveries.

    ENSURES:
    1. Discoveries cite published data sources
    2. Sources are from acceptable repositories/archives
    3. Data quality meets minimum standards
    4. Citations are verifiable and traceable
    """

    def __init__(self):
        # Acceptable data source patterns (more flexible)
        self.repository_patterns = {
            # Sequence databases
            'genbank': r'genbank|accession\s+[a-z0-9]+',
            'ena': r'ena|embl|accession\s+[a-z0-9]+',
            'ddbj': r'ddbj|accession\s+[a-z0-9]+',

            # Protein databases
            'pdb': r'pdb|protein\s+data\s+bank|structure\s+\d[a-z0-9]{3}',
            'uniprot': r'uniprot|swiss-prot|trembl|[a-z0-9]{6}',
            'pfam': r'pfam|pf\d{5}',
            'interpro': r'interpro|ipr\d{5}',

            # Gene expression databases
            'geo': r'geo|gse\d{4}|gsm\d{5}',
            'arrayexpress': r'arrayexpress|e-matab-\d+',
            'sra': r'sra|srr\d{6}|srp\d{4}',

            # Omics databases
            'tcga': r'tcga|cancer\s+genome\s+atlas',
            'gtex': r'gtex|genotype-tissue\s+expression',
            'encode': r'encode|encyclopedia\s+of\s+dna',

            # Pathway/interaction databases
            'kegg': r'kegg|pathway\s+map\d{5}',
            'reactome': r'reactome|r-[a-z]{3}-\d+',
            'biogrid': r'biogrid|interaction\s+\d+',

            # Ontology databases
            'go': r'gene\s+ontology|go:\d{7}',
            'mesh': r'mesh|d\d{5}',
        }

        # Peer-reviewed literature patterns (more flexible)
        self.literature_patterns = {
            'doi': r'doi:\s*10\.\d+/\S+|doi\s+10\.\d+',
            'pmid': r'pmid:\s*\d+|pmid\s+\d+',
            'pmc': r'pmc:\s*pmc\d+|pmc\s+pmc\d+',
            'arxiv': r'arxiv:\s*\d{4}\.\d+',
            'biorxiv': r'biorxiv|bio.*rxiv',
            'pubmed': r'pubmed|pubmed\s+id',
        }

        # High-quality repository indicators
        self.high_quality_indicators = [
            'peer-reviewed', 'curated', 'validated', 'published',
            'journal', 'nature', 'science', 'cell', 'pnas',
            'database', 'repository', 'archive'
        ]

        # Medium-quality indicators
        self.medium_quality_indicators = [
            'preprint', 'bioRxiv', 'arXiv', 'submitted',
            'supplementary', 'supplemental data'
        ]

    def validate_discovery(
        self,
        discovery_text: str,
        evidence_list: List[str] = None
    ) -> DataSourceValidation:
        """
        Validate data sources for a discovery.

        Args:
            discovery_text: The discovery text to analyze
            evidence_list: Optional list of evidence citations

        Returns:
            DataSourceValidation with detailed analysis
        """
        validation = DataSourceValidation(
            is_valid=False,
            confidence=0.0,
            sources_found=[],
            missing_sources=[],
            quality_issues=[],
            recommendations=[]
        )

        # Combine discovery text and evidence for analysis
        analysis_text = discovery_text
        if evidence_list:
            analysis_text += " " + " ".join(evidence_list)

        # Identify data sources
        sources = self._identify_data_sources(analysis_text)
        validation.sources_found = sources

        # Count by type
        validation.peer_reviewed_count = sum(
            1 for s in sources if s.source_type in [
                DataSourceType.PEER_REVIEWED, DataSourceType.PREPRINT
            ]
        )
        validation.repository_count = sum(
            1 for s in sources if s.source_type in [
                DataSourceType.DATA_REPOSITORY, DataSourceType.CURATED_DATABASE
            ]
        )
        validation.unverified_count = sum(
            1 for s in sources if s.quality == DataQuality.UNVERIFIED
        )

        # Calculate data quality score
        validation.data_quality_score = self._calculate_data_quality_score(sources)

        # Determine if valid
        validation.is_valid = self._is_valid_discovery(validation)
        validation.confidence = self._calculate_validation_confidence(validation)

        # Generate recommendations
        validation.recommendations = self._generate_recommendations(validation)

        return validation

    def _identify_data_sources(self, text: str) -> List[DataSource]:
        """Identify data sources mentioned in text"""
        sources = []
        text_lower = text.lower()

        # Check for repository/database mentions
        for repo_name, pattern in self.repository_patterns.items():
            if re.search(pattern, text_lower):
                # Try to extract specific identifier
                identifier = self._extract_identifier(text, pattern)
                if identifier:
                    sources.append(DataSource(
                        source_type=DataSourceType.DATA_REPOSITORY,
                        identifier=identifier,
                        quality=DataQuality.HIGH,
                        description=f"{repo_name.upper()} data source"
                    ))

        # Check for literature citations
        for lit_type, pattern in self.literature_patterns.items():
            if re.search(pattern, text_lower):
                # Try to extract identifier
                identifier = self._extract_identifier(text, pattern)
                if identifier:
                    source_type = DataSourceType.PREPRINT if 'rxiv' in identifier else DataSourceType.PEER_REVIEWED
                    sources.append(DataSource(
                        source_type=source_type,
                        identifier=identifier,
                        quality=DataQuality.HIGH if source_type == DataSourceType.PEER_REVIEWED else DataQuality.MEDIUM,
                        description=f"{lit_type.upper()} citation"
                    ))

        # Check for quality indicators to assess existing sources
        for source in sources:
            source.quality = self._assess_source_quality(text, source)

        return sources

    def _extract_identifier(self, text: str, pattern: str) -> Optional[str]:
        """Extract specific identifier from text using pattern"""
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return None

    def _assess_source_quality(self, text: str, source: DataSource) -> DataQuality:
        """Assess quality of a data source"""
        text_lower = text.lower()

        # Check for high-quality indicators
        if any(indicator in text_lower for indicator in self.high_quality_indicators):
            return DataQuality.HIGH

        # Check for medium-quality indicators
        if any(indicator in text_lower for indicator in self.medium_quality_indicators):
            return DataQuality.MEDIUM

        # Default to LOW if no indicators found
        return DataQuality.LOW

    def _calculate_data_quality_score(self, sources: List[DataSource]) -> float:
        """Calculate overall data quality score (0-1)"""
        if not sources:
            return 0.0

        quality_scores = {
            DataQuality.HIGH: 1.0,
            DataQuality.MEDIUM: 0.7,
            DataQuality.LOW: 0.4,
            DataQuality.UNVERIFIED: 0.0
        }

        total_score = sum(quality_scores.get(s.quality, 0.0) for s in sources)
        return total_score / len(sources)

    def _is_valid_discovery(self, validation: DataSourceValidation) -> bool:
        """Determine if discovery has valid data sources"""
        # Must have at least one source
        if not validation.sources_found:
            return False

        # Must have acceptable data quality
        if validation.data_quality_score < 0.5:
            return False

        # Should have peer-reviewed or repository sources
        if validation.peer_reviewed_count + validation.repository_count == 0:
            return False

        return True

    def _calculate_validation_confidence(self, validation: DataSourceValidation) -> float:
        """Calculate confidence in validation (0-1)"""
        base_confidence = 0.5

        # More sources = higher confidence
        source_count_bonus = min(0.2, len(validation.sources_found) * 0.05)

        # Higher data quality = higher confidence
        quality_bonus = validation.data_quality_score * 0.2

        # Peer-reviewed sources boost confidence
        peer_reviewed_bonus = min(0.1, validation.peer_reviewed_count * 0.03)

        return min(1.0, base_confidence + source_count_bonus + quality_bonus + peer_reviewed_bonus)

    def _generate_recommendations(self, validation: DataSourceValidation) -> List[str]:
        """Generate recommendations for improving data sources"""
        recommendations = []

        if not validation.sources_found:
            recommendations.append("DISCOVERY REQUIRES DATA SOURCES: Add citations to published literature, data repositories, or archives")

        if validation.peer_reviewed_count == 0:
            recommendations.append("ADD PEER-REVIEWED SOURCES: Cite peer-reviewed journal articles to strengthen claims")

        if validation.repository_count == 0:
            recommendations.append("ADD REPOSITORY DATA: Reference data from public repositories (GenBank, PDB, GEO, etc.)")

        if validation.data_quality_score < 0.5:
            recommendations.append("IMPROVE DATA QUALITY: Use higher-quality, curated, or peer-reviewed sources")

        if validation.unverified_count > 0:
            recommendations.append("REMOVE UNVERIFIED SOURCES: Replace unverified claims with published citations")

        return recommendations


def create_data_source_validator() -> DataSourceValidator:
    """Factory function to create data source validator"""
    return DataSourceValidator()


def get_data_source_validator() -> DataSourceValidator:
    """Get singleton instance"""
    global _instance
    if '_instance' not in globals():
        _instance = create_data_source_validator()
    return _instance


# Utility functions

def validate_discovery_data_sources(discovery_text: str, evidence_list: List[str] = None) -> bool:
    """
    Quick validation: Check if discovery has acceptable data sources.

    Returns True if discovery meets data source requirements.
    """
    validator = get_data_source_validator()
    validation = validator.validate_discovery(discovery_text, evidence_list)
    return validation.is_valid


def get_data_source_recommendations(discovery_text: str, evidence_list: List[str] = None) -> List[str]:
    """
    Get recommendations for improving data sources in a discovery.

    Returns list of specific recommendations.
    """
    validator = get_data_source_validator()
    validation = validator.validate_discovery(discovery_text, evidence_list)
    return validation.recommendations
