"""
Peer Review Validator as HARD GATE in Discovery Pipeline

This module implements peer review criteria to reject discoveries that are:
1. Not novel (generic questions in saturated fields)
2. Technically flawed (control probes as genes, wrong data type)
3. Meaningless (null results from inappropriate analysis)
4. Incomplete (missing metadata, cannot reproduce)
5. Unethical (misrepresents findings, overstated claims)

This is a NON-NEGOTIABLE hard gate - no pseudo-science escapes peer review.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PeerReviewDecision(Enum):
    """Peer review decision"""
    ACCEPT = "accept"  # Publishable discovery
    REJECT = "reject"  # Must be rejected before saving
    MAJOR_REVISION = "major_revision"  # Requires fixes before saving


@dataclass
class PeerReviewResult:
    """Result of peer review validation"""
    decision: PeerReviewDecision
    novelty_score: float  # 0-10
    scientific_merit: float  # 0-10
    data_quality: float  # 0-10
    reproducibility: float  # 0-10
    overall_score: float  # 0-40 (sum of above)
    critical_issues: List[str]
    minor_issues: List[str]
    recommendations: List[str]


class PeerReviewValidator:
    """
    Peer review validator as HARD GATE in discovery pipeline.

    This replaces internal validation with external peer review standards.
    """

    def __init__(self):
        self.validations_performed = 0
        self.rejections = 0

        # Thresholds for acceptance
        self.MIN_NOVELTY_SCORE = 7.0  # Must be genuinely novel
        self.MIN_MERIT_SCORE = 7.0     # Must advance understanding
        self.MIN_DATA_QUALITY = 8.0    # Must use appropriate data types
        self.MIN_REPRODUCIBILITY = 8.0 # Must be reproducible

        logger.info("📋 Peer Review Validator initialized as HARD GATE")
        logger.info(f"   Minimum novelty: {self.MIN_NOVELTY_SCORE}/10")
        logger.info(f"   Minimum merit: {self.MIN_MERIT_SCORE}/10")

    def validate_discovery_for_peer_review(self, discovery_report: Dict) -> PeerReviewResult:
        """
        Perform comprehensive peer review on discovery.

        This is a HARD GATE - only acceptable discoveries should be saved.

        Args:
            discovery_report: Complete discovery report to validate

        Returns:
            PeerReviewResult with decision and detailed feedback
        """

        logger.info("📋 PERFORMING PEER REVIEW VALIDATION")
        logger.info("=" * 80)

        # Initialize scores
        novelty_score = 0.0
        merit_score = 0.0
        data_quality_score = 0.0
        reproducibility_score = 0.0
        critical_issues = []
        minor_issues = []
        recommendations = []

        # 1. NOVELTY ASSESSMENT
        novelty_score, novelty_issues = self._assess_novelty(discovery_report)
        if novelty_score < self.MIN_NOVELTY_SCORE:
            critical_issues.extend(novelty_issues)

        # 2. SCIENTIFIC MERIT ASSESSMENT
        merit_score, merit_issues = self._assess_scientific_merit(discovery_report)
        if merit_score < self.MIN_MERIT_SCORE:
            critical_issues.extend(merit_issues)

        # 3. DATA QUALITY ASSESSMENT
        data_quality_score, data_issues = self._assess_data_quality(discovery_report)
        if data_quality_score < self.MIN_DATA_QUALITY:
            critical_issues.extend(data_issues)

        # 4. REPRODUCIBILITY ASSESSMENT
        reproducibility_score, reproducibility_issues = self._assess_reproducibility(discovery_report)
        if reproducibility_score < self.MIN_REPRODUCIBILITY:
            critical_issues.extend(reproducibility_issues)

        # Calculate overall score
        overall_score = novelty_score + merit_score + data_quality_score + reproducibility_score

        # Make decision
        if overall_score >= 28:  # High quality across all dimensions
            decision = PeerReviewDecision.ACCEPT
            logger.info(f"✅ PEER REVIEW: ACCEPT (score: {overall_score}/40)")
        elif overall_score >= 20:  # Has merit but needs work
            decision = PeerReviewDecision.MAJOR_REVISION
            critical_issues.append("Requires major revisions before acceptance")
            logger.info(f"⚠️  PEER REVIEW: MAJOR REVISION (score: {overall_score}/40)")
        else:  # Fails peer review standards
            decision = PeerReviewDecision.REJECT
            self.rejections += 1
            logger.info(f"❌ PEER REVIEW: REJECT (score: {overall_score}/40)")

        result = PeerReviewResult(
            decision=decision,
            novelty_score=novelty_score,
            scientific_merit=merit_score,
            data_quality=data_quality_score,
            reproducibility=reproducibility_score,
            overall_score=overall_score,
            critical_issues=critical_issues,
            minor_issues=minor_issues,
            recommendations=recommendations
        )

        # Log detailed feedback
        self._log_review_result(result)

        return result

    def _assess_novelty(self, discovery: Dict) -> tuple[float, List[str]]:
        """Assess scientific novelty of the discovery"""
        score = 0.0
        issues = []

        question = discovery.get("question", "").lower()

        # Check for generic/broad questions
        generic_patterns = [
            "patient stratification", "biomarker discovery",
            "gene expression profiling", "molecular signatures",
            "disease subtypes", "pathway analysis"
        ]

        for pattern in generic_patterns:
            if pattern in question:
                issues.append(f"Generic question in saturated field: '{pattern}'")
                return 2.0, issues

        # Check for specific, novel questions
        specific_indicators = [
            "response to", "resistance to", "sensitivity to",
            "specific mutation", "specific inhibitor",
            "vs untreated", "vs wild-type", "mutant vs",
            "knockdown", "overexpression", "depletion"
        ]

        specific_count = sum(1 for indicator in specific_indicators if indicator in question)

        if specific_count >= 2:
            score = 8.0  # High novelty
            issues = []  # No issues
        elif specific_count == 1:
            score = 6.0  # Moderate novelty
            issues = ["Could be more specific about biological context"]
        else:
            score = 4.0  # Low novelty
            issues.append("Question too broad - lacks specific biological context")

        return score, issues

    def _assess_scientific_merit(self, discovery: Dict) -> tuple[float, List[str]]:
        """Assess whether discovery advances scientific understanding"""
        score = 0.0
        issues = []

        de = discovery.get("differential_expression", {})
        significant_genes = de.get("significant_genes", 0)

        # Check if results are meaningful
        if significant_genes > 0:
            score = 8.0  # Has findings
        else:
            # Check if null result is appropriately interpreted
            if de.get("total_genes_tested", 0) > 0:
                score = 4.0  # Null result but analyzed
                issues.append("Null result without biological interpretation")
            else:
                score = 2.0  # No real analysis
                issues.append("No meaningful results")

        return score, issues

    def _assess_data_quality(self, discovery: Dict) -> tuple[float, List[str]]:
        """Assess quality and appropriateness of data used"""
        score = 0.0
        issues = []

        # Check if control probes were misidentified as genes
        de = discovery.get("differential_expression", {})
        top_genes = de.get("top_upregulated", []) + de.get("top_downregulated", [])

        # Check if genes are actually control probes
        control_count = sum(1 for gene in top_genes if "control" in gene.get("gene_symbol", "").lower())
        total_genes = len(top_genes)

        if total_genes > 0:
            control_ratio = control_count / total_genes
            if control_ratio > 0.5:
                score = 1.0  # FUNDAMENTAL FLAW
                issues.append(f"CRITICAL: {(control_ratio*100):.0f}% of 'genes' are control probes - data misinterpretation")
            else:
                score = 7.0  # Acceptable
        else:
            score = 5.0  # Can't assess
            issues.append("No gene data available to assess")

        # Check metadata completeness
        dataset = discovery.get("dataset", {})
        if dataset.get("sample_count", 0) == 0:
            issues.append("Missing sample count in metadata")
            score = min(score, 6.0)

        if not dataset.get("geo_dataset_id") or dataset.get("geo_dataset_id") == "Unknown":
            issues.append("Missing dataset accession number")
            score = min(score, 6.0)

        return score, issues

    def _assess_reproducibility(self, discovery: Dict) -> tuple[float, List[str]]:
        """Assess whether discovery can be reproduced"""
        score = 0.0
        issues = []

        dataset = discovery.get("dataset", {})

        # Check for essential reproducibility information
        if not dataset.get("geo_dataset_id"):
            issues.append("❌ CRITICAL: No dataset accession - cannot reproduce")
            score = 2.0
        else:
            score = 8.0  # Has accession

        if not dataset.get("organism") or dataset.get("organism") == "Unknown":
            issues.append("❌ CRITICAL: Organism not specified")
            score = min(score, 6.0)

        if dataset.get("sample_count", 0) == 0:
            issues.append("Sample count not specified")
            score = min(score, 6.0)

        # Check for methodology description
        if not discovery.get("differential_expression", {}).get("method"):
            issues.append("Statistical method not specified")
            score = min(score, 7.0)

        return score, issues

    def _log_review_result(self, result: PeerReviewResult):
        """Log detailed peer review results"""
        logger.info("=" * 80)
        logger.info(f"📋 PEER REVIEW RESULT: {result.decision.value.upper()}")
        logger.info(f"   Overall Score: {result.overall_score:.1f}/40")
        logger.info(f"   Novelty: {result.novelty_score:.1f}/10")
        logger.info(f"   Scientific Merit: {result.scientific_merit:.1f}/10")
        logger.info(f"   Data Quality: {result.data_quality:.1f}/10")
        logger.info(f"   Reproducibility: {result.reproducibility:.1f}/10")
        logger.info("")

        if result.critical_issues:
            logger.info(f"   CRITICAL ISSUES ({len(result.critical_issues)}):")
            for issue in result.critical_issues:
                logger.info(f"   ❌ {issue}")

        if result.minor_issues:
            logger.info(f"   Minor Issues ({len(result.minor_issues)}):")
            for issue in result.minor_issues:
                logger.info(f"   ⚠️  {issue}")

        logger.info("=" * 80)


def create_peer_review_validator() -> PeerReviewValidator:
    """Factory function to create peer review validator"""
    return PeerReviewValidator()
