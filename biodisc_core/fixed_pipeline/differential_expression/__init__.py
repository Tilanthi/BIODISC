"""
Fixed Pipeline: Real Differential Expression Analysis

This module implements actual statistical analysis instead of template filling.

CRITICAL: This generates REAL scientific results:
- Actual gene names with p-values
- Real fold changes
- Statistical testing with proper corrections
- Volcano plot data
- Gene ranking and annotation

NO MORE TEMPLATE-FILLING - EVERYTHING MUST BE REAL DATA.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from statsmodels.stats.multitest import multipletests
import json

logger = logging.getLogger(__name__)


@dataclass
class DifferentialExpressionResult:
    """Results from actual differential expression analysis"""
    gene_id: str
    gene_symbol: str
    log2_fold_change: float
    p_value: float
    fdr_p_value: float
    t_statistic: float
    mean_expression_group1: float
    mean_expression_group2: float
    significant: bool
    regulation: str  # "up" or "down"


@dataclass
class DifferentialExpressionAnalysis:
    """Complete differential expression analysis with real statistics"""

    question: str
    dataset_id: str
    total_genes_tested: int
    significant_genes: int
    upregulated_genes: int
    downregulated_genes: int
    results: List[DifferentialExpressionResult]
    method_used: str
    correction_method: str
    alpha_threshold: float
    volcano_plot_data: List[Dict]

    def get_top_genes(self, n: int = 20, direction: str = "all") -> List[Dict]:
        """Get top N genes by significance"""

        filtered_results = self.results

        if direction == "up":
            filtered_results = [r for r in self.results if r.regulation == "up"]
        elif direction == "down":
            filtered_results = [r for r in self.results if r.regulation == "down"]

        # Sort by p-value
        sorted_results = sorted(filtered_results, key=lambda x: x.p_value)

        top_genes = []
        for result in sorted_results[:n]:
            top_genes.append({
                'gene_symbol': result.gene_symbol,
                'log2_fold_change': result.log2_fold_change,
                'p_value': result.p_value,
                'fdr_p_value': result.fdr_p_value,
                'regulation': result.regulation
            })

        logger.info(f"   get_top_genes returning {len(top_genes)} genes, first 3: {[g['gene_symbol'] for g in top_genes[:3]]}")

        return top_genes

    def generate_results_table(self) -> pd.DataFrame:
        """Generate a pandas DataFrame with all results"""

        data = []
        for result in self.results:
            data.append({
                'Gene_Symbol': result.gene_symbol,
                'Gene_ID': result.gene_id,
                'Log2FC': result.log2_fold_change,
                'P_Value': result.p_value,
                'FDR_P_Value': result.fdr_p_value,
                'T_Statistic': result.t_statistic,
                'Mean_Expr_Group1': result.mean_expression_group1,
                'Mean_Expr_Group2': result.mean_expression_group2,
                'Significant': result.significant,
                'Regulation': result.regulation
            })

        return pd.DataFrame(data)


class DifferentialExpressionAnalyzer:
    """
    Performs actual differential expression analysis using real statistical methods.

    This replaces template-filling with genuine scientific analysis.
    """

    def __init__(self):
        self.analyses_performed = 0
        self.genes_tested_total = 0
        self.significant_genes_total = 0

    def perform_differential_expression_analysis(
        self,
        expression_data: np.ndarray,
        gene_symbols: List[str],
        group_labels: np.ndarray,
        question: str,
        dataset_id: str
    ) -> DifferentialExpressionAnalysis:
        """
        Perform actual differential expression analysis using t-tests with FDR correction.

        Args:
            expression_data: Gene expression matrix (genes x samples)
            gene_symbols: List of gene symbols
            group_labels: Binary group labels for samples (0 = control, 1 = treatment)
            question: The biological question being addressed
            dataset_id: Dataset identifier

        Returns:
            DifferentialExpressionAnalysis with real results
        """

        logger.info(f"🧬 Performing differential expression analysis for {dataset_id}")
        logger.info(f"   Question: {question[:60]}...")
        logger.info(f"   Genes: {len(gene_symbols)}, Samples: {expression_data.shape[1]}")

        self.analyses_performed += 1

        # Validate inputs
        if expression_data.shape[0] != len(gene_symbols):
            raise ValueError("Expression data rows must match gene symbols length")

        if expression_data.shape[1] != len(group_labels):
            raise ValueError("Expression data columns must match group labels length")

        # Perform t-tests for each gene
        results = []
        p_values = []
        log2_fold_changes = []
        t_statistics = []

        group1_indices = np.where(group_labels == 0)[0]
        group2_indices = np.where(group_labels == 1)[0]

        logger.info(f"   Group 1 (control): {len(group1_indices)} samples")
        logger.info(f"   Group 2 (treatment): {len(group2_indices)} samples")

        # Log first few gene symbols to verify real symbols are being used
        if len(gene_symbols) > 0:
            logger.info(f"   First 5 gene symbols received: {gene_symbols[:5]}")
            if gene_symbols[0].startswith('GENE_'):
                logger.warning(f"   ⚠️ WARNING: Received GENE_XXXX format instead of real symbols!")
            else:
                logger.info(f"   ✅ Using real gene symbols")

        for i, gene_symbol in enumerate(gene_symbols):
            # Extract expression values for this gene
            gene_expression = expression_data[i, :]

            # Get group values
            group1_values = gene_expression[group1_indices]
            group2_values = gene_expression[group2_indices]

            # Calculate mean expression
            mean1 = np.mean(group1_values)
            mean2 = np.mean(group2_values)

            # Calculate log2 fold change
            # Add small pseudocount to avoid log(0)
            log2fc = np.log2((mean2 + 1e-6) / (mean1 + 1e-6))

            # Perform t-test
            t_stat, p_value = stats.ttest_ind(group2_values, group1_values)

            # Handle NaN p-values
            if np.isnan(p_value) or np.isinf(p_value):
                p_value = 1.0

            # Store results
            p_values.append(p_value)
            log2_fold_changes.append(log2fc)
            t_statistics.append(t_stat)

        # Convert to arrays
        p_values = np.array(p_values)
        log2_fold_changes = np.array(log2_fold_changes)

        # Perform FDR correction (Benjamini-Hochberg)
        reject, fdr_p_values, _, _ = multipletests(
            p_values,
            alpha=0.05,
            method='fdr_bh'
        )

        # Create result objects
        de_results = []
        significant_count = 0
        upregulated_count = 0
        downregulated_count = 0

        logger.info(f"   Creating results for {len(gene_symbols)} genes")

        for i, gene_symbol in enumerate(gene_symbols):
            # Determine regulation
            if log2_fold_changes[i] > 0:
                regulation = "up"
                if fdr_p_values[i] < 0.05:
                    upregulated_count += 1
            else:
                regulation = "down"
                if fdr_p_values[i] < 0.05:
                    downregulated_count += 1

            # Check significance
            significant = fdr_p_values[i] < 0.05 and reject[i]
            if significant:
                significant_count += 1

            result = DifferentialExpressionResult(
                gene_id=gene_symbol,  # Use real gene symbol as ID
                gene_symbol=gene_symbol,  # Use real gene symbol
                log2_fold_change=log2_fold_changes[i],
                p_value=p_values[i],
                fdr_p_value=fdr_p_values[i],
                t_statistic=t_statistics[i],
                mean_expression_group1=np.mean(expression_data[i, group1_indices]),
                mean_expression_group2=np.mean(expression_data[i, group2_indices]),
                significant=significant,
                regulation=regulation
            )

            de_results.append(result)

        # Log first few results to verify gene symbols
        if len(de_results) > 0:
            logger.info(f"   Sample of results (first 3):")
            for i, r in enumerate(de_results[:3], 1):
                logger.info(f"     {i}. gene_id={r.gene_id}, gene_symbol={r.gene_symbol}")

        # Create volcano plot data
        volcano_data = []
        for result in de_results:
            volcano_data.append({
                'gene_symbol': result.gene_symbol,
                'log2_fold_change': result.log2_fold_change,
                'neg_log10_pvalue': -np.log10(result.p_value + 1e-300),
                'significant': result.significant
            })

        # Create analysis object
        analysis = DifferentialExpressionAnalysis(
            question=question,
            dataset_id=dataset_id,
            total_genes_tested=len(gene_symbols),
            significant_genes=significant_count,
            upregulated_genes=upregulated_count,
            downregulated_genes=downregulated_count,
            results=de_results,
            method_used="t-test",
            correction_method="Benjamini-Hochberg FDR",
            alpha_threshold=0.05,
            volcano_plot_data=volcano_data
        )

        # Update statistics
        self.genes_tested_total += len(gene_symbols)
        self.significant_genes_total += significant_count

        logger.info(f"✅ Analysis complete:")
        logger.info(f"   Total genes tested: {len(gene_symbols)}")
        logger.info(f"   Significant genes (FDR < 0.05): {significant_count}")
        logger.info(f"   Upregulated: {upregulated_count}")
        logger.info(f"   Downregulated: {downregulated_count}")

        return analysis

    def generate_real_gene_expression_data(
        self,
        n_genes: int = 1000,
        n_samples: int = 50,
        n_significant: int = 50,
        effect_size: float = 1.5
    ) -> Tuple[np.ndarray, List[str], np.ndarray]:
        """
        Generate realistic synthetic gene expression data for testing.

        This creates data with known differentially expressed genes
        to validate the analysis pipeline.
        """

        logger.info(f"🧪 Generating synthetic expression data:")
        logger.info(f"   Genes: {n_genes}, Samples: {n_samples}")
        logger.info(f"   Significant genes to simulate: {n_significant}")

        # Generate gene symbols
        gene_symbols = [f"GENE_{i:04d}" for i in range(n_genes)]

        # Generate expression data (log2 scale)
        expression_data = np.random.normal(0, 1, (n_genes, n_samples))

        # Assign samples to groups
        group_labels = np.array([0] * (n_samples // 2) + [1] * (n_samples - n_samples // 2))

        # Add differential expression to selected genes
        significant_indices = np.random.choice(n_genes, n_significant, replace=False)

        for idx in significant_indices:
            # Add effect to treatment group
            treatment_samples = expression_data[idx, group_labels == 1]
            expression_data[idx, group_labels == 1] = treatment_samples + effect_size

        logger.info(f"✅ Synthetic data generated with {n_significant} DE genes")

        return expression_data, gene_symbols, group_labels

    def validate_analysis_results(self, analysis: DifferentialExpressionAnalysis) -> bool:
        """
        Validate that analysis results meet minimum quality standards.

        Returns True if results are valid, False otherwise.
        """

        # Check that we have results
        if len(analysis.results) == 0:
            logger.error("❌ Validation failed: No results")
            return False

        # Check that we have significant genes
        if analysis.significant_genes == 0:
            logger.warning("⚠️  Warning: No significant genes found")
            # This is allowed but flagged

        # Check that FDR values are in valid range
        for result in analysis.results:
            if result.fdr_p_value < 0 or result.fdr_p_value > 1:
                logger.error(f"❌ Validation failed: Invalid FDR value {result.fdr_p_value}")
                return False

            if result.p_value < 0 or result.p_value > 1:
                logger.error(f"❌ Validation failed: Invalid p-value {result.p_value}")
                return False

        # Check that fold changes are reasonable
        for result in analysis.results:
            if abs(result.log2_fold_change) > 20:  # Very high fold change
                logger.warning(f"⚠️  Warning: Extremely high fold change {result.log2_fold_change} for {result.gene_symbol}")

        logger.info("✅ Analysis results validated successfully")
        return True

    def get_statistics(self) -> Dict:
        """Get analyzer statistics"""

        return {
            'analyses_performed': self.analyses_performed,
            'genes_tested_total': self.genes_tested_total,
            'significant_genes_total': self.significant_genes_total,
            'average_significance_rate': (
                self.significant_genes_total / self.genes_tested_total
                if self.genes_tested_total > 0 else 0
            )
        }


def create_differential_expression_analyzer() -> DifferentialExpressionAnalyzer:
    """Factory function to create differential expression analyzer"""
    return DifferentialExpressionAnalyzer()