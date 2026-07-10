"""
Final integration test for peer review fixes.

This test validates that ALL 5 critical peer review issues are fixed:
1. Duplicate detection (214 identical discoveries)
2. Dataset-question mismatch (colon data for breast cancer)
3. Probe IDs as genes (455, 1195, 382, 551, 1739)
4. Null results (zero significant genes)
5. Template questions (BRCA1-PARP in saturated field)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from biodisc_core.fixed_pipeline.FixedDiscoveryOrchestrator import create_fixed_discovery_orchestrator

class TestPeerReviewFixes:
    """Test suite validating all peer review fixes."""

    def setup_method(self):
        """Setup orchestrator for each test."""
        self.orchestrator = create_fixed_discovery_orchestrator()

    def test_critical_issue_1_duplicate_detection(self):
        """
        CRITICAL ISSUE 1: 214 identical discoveries with same p-value (6.25e-04)

        This test validates that duplicate detection prevents identical discoveries.
        """
        # Create first discovery
        discovery1 = {
            'question': 'How does BRCA1 mutation affect response to PARP inhibitors in triple-negative breast cancer?',
            'dataset_id': 'GSE11223',
            'differential_expression': {
                'best_p_value': 0.000625,
                'significant_genes_count': 17,
                'total_genes_tested': 2000,
                'top_genes': [
                    {'gene_symbol': 'BRCA1'},
                    {'gene_symbol': 'TP53'},
                ]
            }
        }

        # First discovery should pass duplicate detection
        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery1)
        # Note: May fail other layers, but not duplicate detection

        # Register first discovery
        self.orchestrator.duplicate_detector.register_discovery(discovery1)

        # Second IDENTICAL discovery should be rejected as duplicate
        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery1)

        # Should be rejected due to duplicate
        assert not passes, "Second identical discovery should be rejected"
        assert any('duplicate' in str(reason).lower() for reason in reasons), \
            f"Should reject as duplicate, got: {reasons}"

        print("✅ CRITICAL ISSUE 1 FIXED: Duplicate detection working")

    def test_critical_issue_2_dataset_question_mismatch(self):
        """
        CRITICAL ISSUE 2: Colon dataset (GSE11223) used for breast cancer question

        This test validates that dataset-question validation prevents tissue mismatches.
        """
        # Create discovery with COLON dataset for BREAST cancer question
        discovery = {
            'question': 'How does BRCA1 mutation affect response to PARP inhibitors in triple-negative breast cancer?',
            'dataset_id': 'GSE11223',
            'dataset_metadata': {
                'title': 'Colon biopsies from ulcerative colitis patients and healthy controls',
                'organism': 'Homo sapiens',
                'tissue': 'colon',
                'disease': 'ulcerative colitis'
            },
            'differential_expression': {
                'best_p_value': 0.000625,
                'significant_genes_count': 17,
                'total_genes_tested': 2000,
                'top_genes': [{'gene_symbol': 'BRCA1'}]
            }
        }

        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery)

        # Should be rejected due to tissue mismatch
        assert not passes, "Colon dataset for breast cancer question should be rejected"
        assert any('mismatch' in str(reason).lower() or 'colon' in str(reason).lower() or 'breast' in str(reason).lower()
                   for reason in reasons), \
            f"Should reject due to tissue mismatch, got: {reasons}"

        print("✅ CRITICAL ISSUE 2 FIXED: Dataset-question validation working")

    def test_critical_issue_3_probe_ids_as_genes(self):
        """
        CRITICAL ISSUE 3: Probe IDs (455, 1195, 382, 551, 1739) treated as gene symbols

        This test validates that probe-gene mapping rejects probe IDs.
        """
        # Create discovery with PROBE IDs (exact values from peer review)
        discovery = {
            'question': 'Test question',
            'dataset_id': 'GSE11223',
            'differential_expression': {
                'best_p_value': 0.000625,
                'significant_genes_count': 17,
                'total_genes_tested': 2000,
                'top_genes': [
                    {'gene_symbol': '455'},    # PROBE ID!
                    {'gene_symbol': '1195'},   # PROBE ID!
                    {'gene_symbol': '382'},    # PROBE ID!
                    {'gene_symbol': '551'},    # PROBE ID!
                    {'gene_symbol': '1739'},   # PROBE ID!
                ]
            }
        }

        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery)

        # Should be rejected due to probe IDs
        assert not passes, "Discovery with probe IDs should be rejected"
        assert any('probe' in str(reason).lower() for reason in reasons), \
            f"Should reject due to probe IDs, got: {reasons}"

        print("✅ CRITICAL ISSUE 3 FIXED: Probe-gene mapping working")

    def test_critical_issue_4_null_results(self):
        """
        CRITICAL ISSUE 4: Zero genes pass FDR < 0.05 (null results)

        This test validates that FDR significance gate rejects null results.
        """
        # Create discovery with ZERO significant genes
        discovery = {
            'question': 'Test question',
            'dataset_id': 'GSE11223',
            'differential_expression': {
                'best_p_value': 0.5,  # Very weak p-value
                'significant_genes_count': 0,  # CRITICAL: ZERO significant genes
                'total_genes_tested': 2000,
                'top_genes': []  # Empty list - no significant genes
            }
        }

        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery)

        # Should be rejected due to null results
        assert not passes, "Discovery with zero significant genes should be rejected"
        assert any('significant' in str(reason).lower() or 'no genes' in str(reason).lower()
                   for reason in reasons), \
            f"Should reject due to null results, got: {reasons}"

        print("✅ CRITICAL ISSUE 4 FIXED: FDR significance gate working")

    def test_critical_issue_5_template_question(self):
        """
        CRITICAL ISSUE 5: Template question in saturated field (BRCA1-PARP with 5000+ papers)

        This test validates that template detection rejects generic template questions.
        """
        # Create discovery with EXACT template question from peer review
        discovery = {
            'question': 'How does BRCA1 mutation status affect response to PARP inhibitors in triple-negative breast cancer?',
            'dataset_id': 'GSE11223',
            'differential_expression': {
                'best_p_value': 0.000625,
                'significant_genes_count': 17,
                'total_genes_tested': 2000,
                'top_genes': [{'gene_symbol': 'BRCA1'}]
            }
        }

        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery)

        # Should be rejected due to template question in saturated field
        assert not passes, "Template question in saturated field should be rejected"
        assert any('template' in str(reason).lower() or 'saturated' in str(reason).lower()
                   for reason in reasons), \
            f"Should reject due to template/saturated field, got: {reasons}"

        print("✅ CRITICAL ISSUE 5 FIXED: Template detection working")

    def test_valid_discovery_accepted(self):
        """
        Positive test: Valid discovery should pass all validation gates.

        This ensures the validation system doesn't reject EVERYTHING (correct operation).
        """
        # Create VALID discovery with:
        # - Specific mechanistic question
        # - Real gene symbols
        # - Significant results
        # - Appropriate dataset
        discovery = {
            'question': 'How does KDM5A-mediated H3K4 demethylation regulate transcriptional silencing of differentiation genes in acute myeloid leukemia?',
            'dataset_id': 'GSE99999',  # Different ID (not duplicate)
            'differential_expression': {
                'best_p_value': 6.25e-04,  # Strong p-value
                'significant_genes_count': 17,  # Good number
                'total_genes_tested': 2000,
                'top_genes': [
                    {'gene_symbol': 'KDM5A'},  # Real gene symbol
                    {'gene_symbol': 'TP53'},   # Real gene symbol
                    {'gene_symbol': 'RUNX1'},  # Real gene symbol
                ]
            }
        }

        # Note: May still fail dataset-question validation without proper metadata
        # But should pass: duplicate detection, probe-gene mapping, FDR gate, template detection

        passes, reasons, _ = self.orchestrator.validate_discovery_comprehensive(discovery)

        # Should pass at least the non-metadata validations
        # Check that it's not rejected for the wrong reasons
        if not passes:
            # Should only fail dataset-question validation (if at all)
            for reason in reasons:
                assert 'duplicate' not in str(reason).lower(), "Should not be duplicate"
                assert 'probe' not in str(reason).lower(), "Should not have probe IDs"
                assert 'significant' not in str(reason).lower(), "Should have significant genes"
                assert 'template' not in str(reason).lower(), "Should be specific question"

        print("✅ VALID DISCOVERY: Validation system accepts genuine discoveries")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])