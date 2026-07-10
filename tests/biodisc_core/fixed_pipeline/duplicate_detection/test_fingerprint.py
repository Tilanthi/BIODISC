"""Test discovery fingerprinting."""
import pytest
from biodisc_core.fixed_pipeline.duplicate_detection import (
    DiscoveryFingerprint, DuplicateDetector, create_duplicate_detector
)

def test_fingerprint_creation():
    """Test fingerprint creation from discovery."""
    discovery = {
        'question': 'How does BRCA1 mutation affect PARP inhibitors?',
        'dataset_id': 'GSE11223',
        'differential_expression': {
            'best_p_value': 0.000625,
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [
                {'gene_symbol': 'BRCA1'},
                {'gene_symbol': 'TP53'}
            ]
        }
    }

    fingerprint = DiscoveryFingerprint.from_discovery(discovery)

    assert fingerprint.question_hash is not None
    assert fingerprint.dataset_hash is not None
    assert len(fingerprint.combined_hash) == 32  # MD5 hash

def test_duplicate_detection():
    """Test duplicate detection."""
    detector = create_duplicate_detector(max_cache_size=100)

    discovery1 = {
        'question': 'How does BRCA1 mutation affect PARP inhibitors?',
        'dataset_id': 'GSE11223',
        'differential_expression': {
            'best_p_value': 0.000625,
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [{'gene_symbol': 'BRCA1'}]
        }
    }

    # First discovery should not be duplicate
    is_dup, reason = detector.check_duplicate(discovery1)
    assert not is_dup
    detector.register_discovery(discovery1)

    # Second identical discovery should be duplicate
    is_dup, reason = detector.check_duplicate(discovery1)
    assert is_dup
    assert "duplicate" in reason.lower()

def test_qd_pair_duplicate():
    """Test same question+dataset pair detection."""
    detector = create_duplicate_detector()

    discovery1 = {
        'question': 'BRCA1 PARP question',
        'dataset_id': 'GSE11223',
        'differential_expression': {
            'best_p_value': 0.001,
            'significant_genes_count': 10,
            'total_genes_tested': 2000,
            'top_genes': [{'gene_symbol': 'GENEA'}]
        }
    }

    discovery2 = {
        'question': 'BRCA1 PARP question',  # Same question
        'dataset_id': 'GSE11223',  # Same dataset
        'differential_expression': {
            'best_p_value': 0.002,  # Different stats
            'significant_genes_count': 15,
            'total_genes_tested': 2000,
            'top_genes': [{'gene_symbol': 'GENEB'}]
        }
    }

    # First not duplicate
    is_dup, _ = detector.check_duplicate(discovery1)
    assert not is_dup
    detector.register_discovery(discovery1)

    # Second should be duplicate (same Q+D pair)
    is_dup, reason = detector.check_duplicate(discovery2)
    assert is_dup
    assert "same question+dataset" in reason.lower()

def test_identical_statistical_profile():
    """Test detection of identical statistical profiles."""
    detector = create_duplicate_detector()

    discovery1 = {
        'question': 'Question A',
        'dataset_id': 'GSE00001',
        'differential_expression': {
            'best_p_value': 0.000625,  # Same p-value
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [{'gene_symbol': 'GENEX'}]
        }
    }

    discovery2 = {
        'question': 'Question B',  # Different question
        'dataset_id': 'GSE99999',  # Different dataset
        'differential_expression': {
            'best_p_value': 0.000625,  # IDENTICAL p-value (suspicious)
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [{'gene_symbol': 'GENEY'}]
        }
    }

    # First not duplicate
    is_dup, _ = detector.check_duplicate(discovery1)
    assert not is_dup
    detector.register_discovery(discovery1)

    # Second should be duplicate (identical stats)
    is_dup, reason = detector.check_duplicate(discovery2)
    assert is_dup
    assert "statistical profile" in reason.lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
