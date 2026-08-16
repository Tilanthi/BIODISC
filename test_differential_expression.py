#!/usr/bin/env python3
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
"""
Test script for real differential expression analysis

This tests that the new system generates REAL scientific results:
- Actual gene names
- Real p-values
- Real fold changes
- Statistical testing
- NOT template filling
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
from biodisc_core.fixed_pipeline.differential_expression import create_differential_expression_analyzer

def test_differential_expression():
    """Test the differential expression analysis system"""

    print("=" * 80)
    print("TESTING REAL DIFFERENTIAL EXPRESSION ANALYSIS")
    print("=" * 80)

    analyzer = create_differential_expression_analyzer()

    # Generate synthetic data
    print("\n🧪 Step 1: Generate synthetic expression data...")
    expression_data, gene_symbols, group_labels = analyzer.generate_real_gene_expression_data(
        n_genes=1000,
        n_samples=50,
        n_significant=50,
        effect_size=1.5
    )

    print(f"✅ Data generated:")
    print(f"   Expression matrix: {expression_data.shape}")
    print(f"   Gene symbols: {len(gene_symbols)}")
    print(f"   Group labels: {len(group_labels)}")
    print(f"   Group 1 samples: {np.sum(group_labels == 0)}")
    print(f"   Group 2 samples: {np.sum(group_labels == 1)}")

    # Perform analysis
    print("\n🧬 Step 2: Perform differential expression analysis...")
    question = "How does gene expression change in cancer cells vs normal cells?"
    dataset_id = "TEST_DATA_001"

    analysis = analyzer.perform_differential_expression_analysis(
        expression_data=expression_data,
        gene_symbols=gene_symbols,
        group_labels=group_labels,
        question=question,
        dataset_id=dataset_id
    )

    # Validate results
    print("\n✅ Step 3: Validate analysis results...")
    is_valid = analyzer.validate_analysis_results(analysis)

    if not is_valid:
        print("❌ VALIDATION FAILED")
        return

    # Display results
    print("\n📊 Step 4: Display REAL results...")

    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total genes tested: {analysis.total_genes_tested}")
    print(f"Significant genes (FDR < 0.05): {analysis.significant_genes}")
    print(f"Upregulated genes: {analysis.upregulated_genes}")
    print(f"Downregulated genes: {analysis.downregulated_genes}")
    print(f"Method: {analysis.method_used}")
    print(f"Correction: {analysis.correction_method}")

    # Get top genes
    print("\n" + "=" * 80)
    print("TOP 20 UPREGULATED GENES")
    print("=" * 80)

    top_up = analysis.get_top_genes(n=20, direction="up")
    print(f"{'Gene Symbol':<15} {'Log2FC':<10} {'P-Value':<12} {'FDR':<12}")
    print("-" * 80)

    for gene in top_up[:10]:  # Show top 10
        print(f"{gene['gene_symbol']:<15} {gene['log2_fold_change']:>8.3f}   {gene['p_value']:>.2e}   {gene['fdr_p_value']:>.2e}")

    print("\n" + "=" * 80)
    print("TOP 20 DOWNREGULATED GENES")
    print("=" * 80)

    top_down = analysis.get_top_genes(n=20, direction="down")
    print(f"{'Gene Symbol':<15} {'Log2FC':<10} {'P-Value':<12} {'FDR':<12}")
    print("-" * 80)

    for gene in top_down[:10]:  # Show top 10
        print(f"{gene['gene_symbol']:<15} {gene['log2_fold_change']:>8.3f}   {gene['p_value']:>.2e}   {gene['fdr_p_value']:>.2e}")

    # Show that these are REAL results, not templates
    print("\n" + "=" * 80)
    print("VALIDATION: REAL RESULTS vs TEMPLATES")
    print("=" * 80)

    checks = [
        ("Has gene symbols", any(g['gene_symbol'] != '' for g in top_up)),
        ("Has p-values", all(g['p_value'] > 0 for g in top_up)),
        ("Has FDR values", all(0 <= g['fdr_p_value'] <= 1 for g in top_up)),
        ("Has fold changes", all(g['log2_fold_change'] != 0 for g in top_up)),
        ("Not template text", all('template' not in str(g).lower() for g in top_up)),
    ]

    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"{status} {check_name}")

    # Show analyzer statistics
    stats = analyzer.get_statistics()
    print("\n" + "=" * 80)
    print("ANALYZER STATISTICS")
    print("=" * 80)
    print(f"Analyses performed: {stats['analyses_performed']}")
    print(f"Total genes tested: {stats['genes_tested_total']}")
    print(f"Total significant genes: {stats['significant_genes_total']}")
    print(f"Average significance rate: {stats['average_significance_rate']:.1%}")

    print("\n✅ DIFFERENTIAL EXPRESSION ANALYSIS TEST COMPLETE")

if __name__ == "__main__":
    test_differential_expression()