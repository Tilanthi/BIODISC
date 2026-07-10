"""FDR significance gate for discovery pipeline."""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SignificanceValidationResult:
    """Result of significance validation."""

    passes_significance_gate: bool
    significance_score: float  # 0-10
    reason: str
    significant_genes_count: int
    total_genes_tested: int
    best_fdr: float
    recommendations: List[str]

class SignificanceValidator:
    """Validate statistical significance before allowing discovery publication."""

    def __init__(self):
        self.validations = 0
        self.rejections = 0

        # MINIMUM requirements
        self.MIN_FDR_THRESHOLD = 0.05  # FDR < 0.05 required
        self.MIN_SIGNIFICANT_GENES = 3  # At least 3 genes pass FDR
        self.MIN_BEST_FDR = 0.01  # Best gene should have FDR < 0.01

        logger.info("📊 SignificanceValidator initialized as HARD GATE")
        logger.info(f"   Minimum FDR threshold: {self.MIN_FDR_THRESHOLD}")
        logger.info(f"   Minimum significant genes: {self.MIN_SIGNIFICANT_GENES}")
        logger.info(f"   Minimum best FDR: {self.MIN_BEST_FDR}")

    def validate_significance(
        self,
        de_results: Dict
    ) -> SignificanceValidationResult:
        """
        Validate if results meet minimum significance requirements.

        Args:
            de_results: Differential expression results with FDR values

        Returns:
            SignificanceValidationResult with decision and details
        """

        logger.info("📊 VALIDATING STATISTICAL SIGNIFICANCE")

        self.validations += 1

        # Extract key metrics
        significant_genes = de_results.get('significant_genes_count', 0)
        total_genes = de_results.get('total_genes_tested', 0)

        # Get FDR values
        top_genes = de_results.get('top_genes', [])
        fdr_values = [g.get('fdr_p_value', 1.0) for g in top_genes if 'fdr_p_value' in g]

        best_fdr = min(fdr_values) if fdr_values else 1.0

        logger.info(f"   Total genes tested: {total_genes}")
        logger.info(f"   Significant genes (FDR < 0.05): {significant_genes}")
        logger.info(f"   Best FDR: {best_fdr:.2e}")

        # Calculate significance score
        score = self._calculate_significance_score(
            significant_genes, total_genes, best_fdr
        )

        # Check requirements
        issues = []
        recommendations = []

        # Check 1: Any significant genes?
        if significant_genes == 0:
            issues.append("No genes pass FDR < 0.05 threshold")
            recommendations.append("Analysis returned null results - cannot publish as discovery")

        # Check 2: Minimum significant genes?
        if significant_genes < self.MIN_SIGNIFICANT_GENES:
            issues.append(f"Only {significant_genes} significant genes (minimum: {self.MIN_SIGNIFICANT_GENES})")
            recommendations.append("Insufficient statistical power - increase sample size or effect size")

        # Check 3: Best FDR threshold?
        if best_fdr >= self.MIN_BEST_FDR:
            issues.append(f"Best FDR ({best_fdr:.2e}) exceeds minimum ({self.MIN_BEST_FDR})")
            recommendations.append("Top hit not significant enough - may be false positive")

        # Make decision
        passes_gate = (
            significant_genes >= self.MIN_SIGNIFICANT_GENES and
            best_fdr < self.MIN_BEST_FDR
        )

        if not passes_gate:
            self.rejections += 1
            logger.error(f"❌ SIGNIFICANCE GATE: FAILED")
            logger.error(f"   Issues: {issues}")
        else:
            logger.info(f"✅ SIGNIFICANCE GATE: PASSED (score: {score}/10)")

        return SignificanceValidationResult(
            passes_significance_gate=passes_gate,
            significance_score=score,
            reason="; ".join(issues) if issues else "Statistical significance confirmed",
            significant_genes_count=significant_genes,
            total_genes_tested=total_genes,
            best_fdr=best_fdr,
            recommendations=recommendations
        )

    def _calculate_significance_score(
        self,
        significant_genes: int,
        total_genes: int,
        best_fdr: float
    ) -> float:
        """Calculate significance score (0-10)."""

        score = 0.0

        # Base score for having any significant genes
        if significant_genes > 0:
            score += 3.0

        # More significant genes = higher score
        if significant_genes >= 3:
            score += 2.0
        if significant_genes >= 10:
            score += 2.0
        if significant_genes >= 50:
            score += 1.0

        # Best FDR score
        if best_fdr < 0.001:
            score += 2.0
        elif best_fdr < 0.01:
            score += 1.5
        elif best_fdr < 0.05:
            score += 1.0

        return min(score, 10.0)

    def get_statistics(self) -> Dict:
        """Get validation statistics."""
        return {
            'validations_performed': self.validations,
            'rejections': self.rejections,
            'rejection_rate': f"{(self.rejections / max(self.validations, 1)) * 100:.2f}%"
        }
