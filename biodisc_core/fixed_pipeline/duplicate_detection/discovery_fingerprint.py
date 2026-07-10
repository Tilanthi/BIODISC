"""Discovery fingerprinting for duplicate detection."""
import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class DiscoveryFingerprint:
    """Statistical fingerprint of a discovery for duplicate detection."""

    question_hash: str  # Hash of question text (normalized)
    dataset_hash: str  # Hash of dataset ID
    statistical_hash: str  # Hash of key statistical measures
    gene_set_hash: str  # Hash of top 10 gene symbols
    combined_hash: str  # Master hash for duplicate detection

    @classmethod
    def from_discovery(cls, discovery: Dict[str, Any]) -> 'DiscoveryFingerprint':
        """Create fingerprint from discovery report."""

        # Extract key fields
        question = discovery.get('question', '').lower().strip()
        dataset_id = discovery.get('dataset_id', '')

        # Statistical signature
        de_results = discovery.get('differential_expression', {})
        best_p_value = de_results.get('best_p_value', 0.0)
        significant_count = de_results.get('significant_genes_count', 0)
        total_genes = de_results.get('total_genes_tested', 0)

        # Gene signature (top 10 if available)
        top_genes = de_results.get('top_genes', [])
        gene_list = sorted([g.get('gene_symbol', '') for g in top_genes[:10]])

        # Create hashes
        question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        dataset_hash = hashlib.md5(dataset_id.encode()).hexdigest()[:8]

        # Statistical signature (precision to 4 decimals to catch duplicates)
        sig_data = f"{best_p_value:.4f}_{significant_count}_{total_genes}"
        statistical_hash = hashlib.md5(sig_data.encode()).hexdigest()[:8]

        # Gene signature
        gene_data = '_'.join(gene_list)
        gene_set_hash = hashlib.md5(gene_data.encode()).hexdigest()[:8]

        # Combined master hash
        combined = f"{question_hash}_{dataset_hash}_{statistical_hash}_{gene_set_hash}"
        combined_hash = hashlib.md5(combined.encode()).hexdigest()

        logger.info(f"🔑 Fingerprint created: {combined_hash[:12]}...")
        logger.info(f"   Question: {question_hash}, Dataset: {dataset_hash}")
        logger.info(f"   Stats: {statistical_hash}, Genes: {gene_set_hash}")

        return cls(
            question_hash=question_hash,
            dataset_hash=dataset_hash,
            statistical_hash=statistical_hash,
            gene_set_hash=gene_set_hash,
            combined_hash=combined_hash
        )
