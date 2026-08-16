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
"""Test integration of 5-layer validation system."""
import pytest
from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import create_fixed_discovery_orchestrator

def test_comprehensive_validation_rejects_duplicate():
    """Test that duplicate discoveries are rejected."""
    orchestrator = create_fixed_discovery_orchestrator()

    # Create first discovery with realistic data and complete metadata
    discovery1 = {
        'question': 'How does novel gene X affect pathway Y in cancer?',
        'dataset_id': 'GSE11223',
        'dataset': {  # Complete dataset metadata for validation
            'title': 'Gene expression in cancer cell lines treated with drug X',
            'organism': 'Human',
            'tissue': 'Breast cancer',
            'data_type': 'Transcriptomics'
        },
        'differential_expression': {
            'best_p_value': 6.25e-04,
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [
                {'gene_symbol': 'TP53', 'p_value': 6.25e-04, 'fdr_p_value': 0.003},
                {'gene_symbol': 'BRCA1', 'p_value': 0.001, 'fdr_p_value': 0.008}
            ]
        }
    }

    passes, _, _ = orchestrator.validate_discovery_comprehensive(discovery1)
    assert passes  # First discovery passes
    orchestrator.duplicate_detector.register_discovery(discovery1)

    # Second identical discovery should be rejected
    passes, reasons, _ = orchestrator.validate_discovery_comprehensive(discovery1)
    assert not passes
    assert any('duplicate' in r.lower() for r in reasons)

def test_comprehensive_validation_rejects_probe_ids():
    """Test that probe IDs are rejected (critical peer review fix)."""
    orchestrator = create_fixed_discovery_orchestrator()

    discovery = {
        'question': 'Test question',
        'dataset_id': 'GSE11223',
        'differential_expression': {
            'best_p_value': 0.001,
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [
                {'gene_symbol': '455'},  # Probe ID!
                {'gene_symbol': '1195'},
            ]
        }
    }

    passes, reasons, _ = orchestrator.validate_discovery_comprehensive(discovery)

    # Should reject due to probe IDs
    assert not passes
    assert any('probe' in r.lower() for r in reasons)

def test_comprehensive_validation_rejects_null_results():
    """Test that null results are rejected (critical peer review fix)."""
    orchestrator = create_fixed_discovery_orchestrator()

    discovery = {
        'question': 'Test question',
        'dataset_id': 'GSE11223',
        'differential_expression': {
            'best_p_value': 0.5,  # Very weak
            'significant_genes_count': 0,  # CRITICAL: Zero significant genes
            'total_genes_tested': 2000,
            'top_genes': []  # Empty
        }
    }

    passes, reasons, _ = orchestrator.validate_discovery_comprehensive(discovery)

    # Should reject due to null results
    assert not passes
    assert any('significant' in r.lower() or 'no genes' in r.lower() for r in reasons)

def test_comprehensive_validation_rejects_template_question():
    """Test that template questions are rejected (critical peer review fix)."""
    orchestrator = create_fixed_discovery_orchestrator()

    discovery = {
        'question': 'How does BRCA1 mutation affect response to PARP inhibitors?',  # Exact template from peer review
        'dataset_id': 'GSE11223',
        'differential_expression': {
            'best_p_value': 0.000625,
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [{'gene_symbol': 'BRCA1'}]
        }
    }

    passes, reasons, _ = orchestrator.validate_discovery_comprehensive(discovery)

    # Should reject due to template question in saturated field
    assert not passes or any('template' in r.lower() or 'saturated' in r.lower() for r in reasons)

def test_comprehensive_validation_accepts_valid_discovery():
    """Test that valid discoveries pass all gates."""
    orchestrator = create_fixed_discovery_orchestrator()

    discovery = {
        'question': 'How does novel epigenetic regulator X control cancer cell metabolism?',
        'dataset_id': 'GSE99999',  # Different ID
        'dataset': {  # Complete dataset metadata for validation
            'title': 'Epigenetic regulation in cancer metabolism',
            'organism': 'Human',
            'tissue': 'Leukemia',
            'data_type': 'Transcriptomics'
        },
        'differential_expression': {
            'best_p_value': 6.25e-04,
            'significant_genes_count': 17,
            'total_genes_tested': 2000,
            'top_genes': [
                {'gene_symbol': 'KDM5A', 'p_value': 6.25e-04, 'fdr_p_value': 0.003},  # Real gene symbol
                {'gene_symbol': 'TP53', 'p_value': 0.001, 'fdr_p_value': 0.008},
                {'gene_symbol': 'MYC', 'p_value': 0.002, 'fdr_p_value': 0.01}
            ]
        }
    }

    passes, reasons, _ = orchestrator.validate_discovery_comprehensive(discovery)

    # Should pass all validation gates
    assert passes
    assert len(reasons) == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
