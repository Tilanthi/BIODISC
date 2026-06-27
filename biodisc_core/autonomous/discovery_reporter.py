"""
Discovery Reporting System

Manages reporting of validated discoveries back to user.
Generates comprehensive reports with insights and recommendations.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

from .config import (
    AutonomousConfig,
    Discovery,
    DiscoveryReport
)

logger = logging.getLogger(__name__)


class DiscoveryReporter:
    """
    Report validated discoveries to user in appropriate format.

    This system aggregates discoveries, categorizes them, generates insights,
    and produces comprehensive reports for the user.
    """

    def __init__(self, config: AutonomousConfig):
        """
        Initialize discovery reporter.

        Args:
            config: Autonomous system configuration
        """
        self.config = config

        # Report history
        self.report_history: List[DiscoveryReport] = []
        self.discovery_count = 0

        logger.info("Discovery Reporter initialized")

    def report_discoveries(self, discoveries: List[Discovery]) -> DiscoveryReport:
        """
        Generate comprehensive discovery report.

        Args:
            discoveries: List of validated discoveries to report

        Returns:
            DiscoveryReport with comprehensive analysis
        """
        try:
            logger.info(f"Generating report for {len(discoveries)} discoveries")

            # Categorize discoveries
            categorized = self._categorize_discoveries(discoveries)

            # Generate insights
            insights = self._generate_insights(discoveries)

            # Generate recommendations
            recommendations = self._generate_recommendations(discoveries)

            # Calculate quality metrics
            average_confidence = sum(d.confidence for d in discoveries) / len(discoveries) if discoveries else 0
            average_novelty = sum(d.overall_score for d in discoveries) / len(discoveries) if discoveries else 0

            # Create report
            report = DiscoveryReport(
                timestamp=datetime.now(),
                total_discoveries=len(discoveries),
                high_impact_discoveries=[d for d in discoveries if d.overall_score > self.config.notification_threshold_impact],
                categorized_discoveries=categorized,
                insights_generated=insights,
                recommendations=recommendations,
                average_confidence=average_confidence,
                average_novelty=average_novelty,
                validation_rate=1.0  # Only validated discoveries are reported
            )

            # Store report
            self.report_history.append(report)
            self.discovery_count += len(discoveries)

            logger.info(f"Discovery report generated: {len(discoveries)} discoveries, {len(insights)} insights")

            return report

        except Exception as e:
            logger.error(f"Error generating discovery report: {e}")
            # Return minimal report on error
            return DiscoveryReport(
                timestamp=datetime.now(),
                total_discoveries=len(discoveries),
                high_impact_discoveries=[],
                categorized_discoveries={},
                insights_generated=[],
                recommendations=[],
                average_confidence=0.0,
                average_novelty=0.0,
                validation_rate=0.0
            )

    def _categorize_discoveries(self, discoveries: List[Discovery]) -> Dict[str, List[Discovery]]:
        """
        Categorize discoveries by type and domain.

        Args:
            discoveries: List of discoveries to categorize

        Returns:
            Dictionary of categorized discoveries
        """
        categorized = defaultdict(list)

        for discovery in discoveries:
            # By question type
            question_type = discovery.question_type or 'general'
            categorized[f"type_{question_type}"].append(discovery)

            # By domain
            domain = discovery.domain or 'general'
            categorized[f"domain_{domain}"].append(discovery)

            # By impact level
            if discovery.overall_score > 0.8:
                categorized["high_impact"].append(discovery)
            elif discovery.overall_score > 0.6:
                categorized["medium_impact"].append(discovery)
            else:
                categorized["lower_impact"].append(discovery)

        return dict(categorized)

    def _generate_insights(self, discoveries: List[Discovery]) -> List[str]:
        """
        Generate insights from discoveries.

        Args:
            discoveries: List of discoveries to analyze

        Returns:
            List of generated insights
        """
        insights = []

        if not discoveries:
            return insights

        # Insight 1: Domain distribution
        domain_counts = defaultdict(int)
        for discovery in discoveries:
            domain_counts[discovery.domain] += 1

        if domain_counts:
            top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_domains:
                domains_str = ", ".join(f"{d}({c})" for d, c in top_domains)
                insights.append(f"Primary discovery domains: {domains_str}")

        # Insight 2: Question patterns
        question_types = defaultdict(int)
        for discovery in discoveries:
            question_types[discovery.question_type] += 1

        if question_types:
            top_type = max(question_types.items(), key=lambda x: x[1])
            insights.append(f"Most common question type: {top_type[0]} ({top_type[1]} discoveries)")

        # Insight 3: Quality assessment
        high_quality_count = sum(1 for d in discoveries if d.overall_score > 0.8)
        if high_quality_count > 0:
            percentage = (high_quality_count / len(discoveries)) * 100
            insights.append(f"{percentage:.0f}% of discoveries are high quality (>0.8 score)")

        # Insight 4: Novelty assessment
        high_novelty_count = sum(1 for d in discoveries if d.novelty_score > 0.7)
        if high_novelty_count > 0:
            percentage = (high_novelty_count / len(discoveries)) * 100
            insights.append(f"{percentage:.0f}% of discoveries show high novelty")

        # Insight 5: Cross-domain insights
        cross_domain = [d for d in discoveries if d.domain == 'cross_domain']
        if cross_domain:
            insights.append(f"{len(cross_domain)} cross-domain discoveries suggest integration opportunities")

        return insights

    def _generate_recommendations(self, discoveries: List[Discovery]) -> List[str]:
        """
        Generate recommendations based on discoveries.

        Args:
            discoveries: List of discoveries to analyze

        Returns:
            List of recommendations
        """
        recommendations = []

        if not discoveries:
            return recommendations

        # Recommendation 1: Research directions
        high_impact = [d for d in discoveries if d.overall_score > 0.8]
        if high_impact:
            recommendations.append(f"Prioritize experimental validation of {len(high_impact)} high-impact discoveries")

        # Recommendation 2: Domain focus
        domain_counts = defaultdict(int)
        for discovery in discoveries:
            domain_counts[discovery.domain] += 1

        if domain_counts:
            top_domain = max(domain_counts.items(), key=lambda x: x[1])
            recommendations.append(f"Consider increased focus on {top_domain[0]} domain ({top_domain[1]} discoveries)")

        # Recommendation 3: Validation strategies
        untested = [d for d in discoveries if d.testability < 0.5]
        if untested:
            recommendations.append(f"Develop experimental approaches for {len(untested)} less-testable discoveries")

        # Recommendation 4: Cross-domain synthesis
        cross_domain = [d for d in discoveries if d.domain == 'cross_domain']
        if len(cross_domain) > 2:
            recommendations.append("Synthesize cross-domain discoveries into integrated framework")

        # Recommendation 5: Literature review
        novel_discoveries = [d for d in discoveries if d.novelty_score > 0.7]
        if novel_discoveries:
            recommendations.append(f"Conduct literature review for {len(novel_discoveries)} novel discoveries")

        return recommendations

    def get_summary_report(self) -> str:
        """Get summary of all discovery reports"""
        if not self.report_history:
            return "No discoveries reported yet"

        latest_report = self.report_history[-1]
        return latest_report.generate_summary()

    def get_statistics(self) -> Dict[str, Any]:
        """Get reporting statistics"""
        return {
            'total_reports': len(self.report_history),
            'total_discoveries_reported': self.discovery_count,
            'latest_report_count': self.report_history[-1].total_discoveries if self.report_history else 0,
            'average_discoveries_per_report': self.discovery_count / len(self.report_history) if self.report_history else 0
        }