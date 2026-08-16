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
"""Test FDR significance gating."""
import pytest
from biodisc_core.fixed_pipeline.fdr_significance_gate import (
    create_significance_validator,
    SignificanceValidationResult
)

def test_null_results_rejection():
    """Test rejection of null results (zero significant genes)."""
    validator = create_significance_validator()

    de_results = {
        'significant_genes_count': 0,  # CRITICAL: No significant genes
        'total_genes_tested': 2000,
        'top_genes': []  # Empty
    }

    result = validator.validate_significance(de_results)

    # Should REJECT - zero significant genes
    assert not result.passes_significance_gate
    assert result.significant_genes_count == 0
    assert 'No genes pass' in result.reason
    assert result.significance_score < 6.0

def test_insufficient_significant_genes():
    """Test rejection with too few significant genes."""
    validator = create_significance_validator()

    de_results = {
        'significant_genes_count': 1,  # Only 1 gene (minimum is 3)
        'total_genes_tested': 2000,
        'top_genes': [
            {'gene_symbol': 'GENEA', 'fdr_p_value': 0.03}
        ]
    }

    result = validator.validate_significance(de_results)

    # Should REJECT - only 1 significant gene
    assert not result.passes_significance_gate
    assert 'Only 1 significant' in result.reason
    assert 'minimum: 3' in result.reason

def test_weak_best_fdr():
    """Test rejection with weak best FDR."""
    validator = create_significance_validator()

    de_results = {
        'significant_genes_count': 5,  # Enough genes
        'total_genes_tested': 2000,
        'top_genes': [
            {'gene_symbol': 'GENEA', 'fdr_p_value': 0.02},  # Best FDR > 0.01
            {'gene_symbol': 'GENEB', 'fdr_p_value': 0.04},
        ]
    }

    result = validator.validate_significance(de_results)

    # Should REJECT - best FDR too weak
    assert not result.passes_significance_gate
    assert 'Best FDR' in result.reason
    assert 'exceeds minimum' in result.reason

def test_strong_significance():
    """Test acceptance with strong statistical significance."""
    validator = create_significance_validator()

    de_results = {
        'significant_genes_count': 17,  # Good number
        'total_genes_tested': 2000,
        'top_genes': [
            {'gene_symbol': 'BRCA1', 'fdr_p_value': 6.25e-04},  # Strong FDR
            {'gene_symbol': 'TP53', 'fdr_p_value': 0.001},
        ]
    }

    result = validator.validate_significance(de_results)

    # Should PASS - strong significance
    assert result.passes_significance_gate
    assert result.significance_score >= 7.0
    assert 'confirmed' in result.reason.lower()

def test_very_strong_significance():
    """Test acceptance with very strong significance."""
    validator = create_significance_validator()

    de_results = {
        'significant_genes_count': 150,  # Very strong
        'total_genes_tested': 2000,
        'top_genes': [
            {'gene_symbol': 'GENEA', 'fdr_p_value': 1e-10},  # Extremely strong
            {'gene_symbol': 'GENEB', 'fdr_p_value': 1e-8},
        ]
    }

    result = validator.validate_significance(de_results)

    # Should PASS with high score
    assert result.passes_significance_gate
    assert result.significance_score >= 9.0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
