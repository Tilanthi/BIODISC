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
Fixed Pipeline: External Validation System

This module implements EXTERNAL validation instead of self-generated metrics.

CRITICAL FIXES:
- NO self-generated confidence scores
- NO self-generated novelty scores
- NO circular validation
- ONLY external peer review and validation
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass
class ExternalValidation:
    """External validation result (NO SELF-SCORING)"""

    discovery_id: str
    validation_status: ValidationStatus
    reviewer_id: Optional[str]  # External reviewer ID
    validation_timestamp: Optional[float]
    validation_comments: Optional[str]
    external_reviewers: List[str]
    reproducibility_status: str
    statistical_validation: str
    biological_validation: str

    # NO self-generated scores - these are set by EXTERNAL reviewers only
    external_novelty_score: Optional[float] = None  # Set by external reviewers
    external_confidence_score: Optional[float] = None  # Set by external reviewers
    peer_review_verdict: Optional[str] = None  # Set by external reviewers


class ExternalValidationSystem:
    """
    External validation system that prevents self-scoring and circular validation.

    KEY PRINCIPLE: The system cannot judge its own work.
    """

    def __init__(self):
        self.validations_completed = 0
        self.validations_rejected = 0
        self.validations_approved = 0
        self.external_reviewers = []

    def submit_for_external_validation(
        self,
        discovery_data: Dict,
        external_reviewer_ids: List[str]
    ) -> ExternalValidation:
        """
        Submit discovery for EXTERNAL validation (no self-scoring).

        This prevents the circular validation that plagued the previous pipeline.
        """

        discovery_id = discovery_data.get('discovery_id', 'unknown')

        logger.info(f"📨 Submitting discovery {discovery_id} for EXTERNAL validation")
        logger.info(f"   External reviewers: {external_reviewer_ids}")

        # Create external validation object
        validation = ExternalValidation(
            discovery_id=discovery_id,
            validation_status=ValidationStatus.PENDING,
            reviewer_id=None,  # Will be assigned by external system
            validation_timestamp=None,  # Will be set by external reviewer
            validation_comments=None,  # Will be provided by external reviewer
            external_reviewers=external_reviewer_ids,
            reproducibility_status="pending",
            statistical_validation="pending",
            biological_validation="pending"
        )

        logger.info("✅ Discovery submitted for external validation")
        logger.info("⚠️  NO SELF-SCORING - External validation required")

        return validation

    def validate_results_integrity(self, discovery_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate that results have actual scientific content.

        This prevents template-filled pseudo-science from being validated.
        """

        logger.info("🔍 Validating results integrity...")

        issues = []
        warnings = []

        # Check for actual gene names
        has_gene_names = self._check_gene_names(discovery_data)
        if not has_gene_names:
            issues.append("❌ No actual gene names found - template filling detected")

        # Check for p-values
        has_pvalues = self._check_pvalues(discovery_data)
        if not has_pvalues:
            issues.append("❌ No p-values found - claims statistical testing without results")

        # Check for fold changes
        has_fold_changes = self._check_fold_changes(discovery_data)
        if not has_fold_changes:
            issues.append("❌ No fold changes found - claims analysis without magnitude")

        # Check for pathway results
        has_pathways = self._check_pathway_results(discovery_data)
        if not has_pathways:
            warnings.append("⚠️  No pathway analysis results")

        # Check for self-generated scores (BANNED)
        has_self_scores = self._check_self_generated_scores(discovery_data)
        if has_self_scores:
            issues.append("❌ Self-generated confidence/novelty scores detected - BANNED")

        # Check for template text
        has_template_text = self._check_template_text(discovery_data)
        if has_template_text:
            issues.append("❌ Template text detected - not actual analysis")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info("✅ Results integrity validation passed")
        else:
            logger.error("❌ Results integrity validation FAILED:")
            for issue in issues:
                logger.error(f"   {issue}")

        return is_valid, issues + warnings

    def _check_gene_names(self, data: Dict) -> bool:
        """Check for actual gene names (not template text)"""
        # Look for gene symbols in results
        results = data.get('results', [])
        if not results:
            return False

        # Check if we have actual gene symbols
        for result in results:
            gene_symbol = result.get('gene_symbol', '')
            if gene_symbol and not gene_symbol.startswith('GENE_'):
                return True

        return False

    def _check_pvalues(self, data: Dict) -> bool:
        """Check for actual p-values"""
        results = data.get('results', [])
        if not results:
            return False

        for result in results:
            p_value = result.get('p_value', None)
            if p_value is not None and 0 <= p_value <= 1:
                return True

        return False

    def _check_fold_changes(self, data: Dict) -> bool:
        """Check for actual fold changes"""
        results = data.get('results', [])
        if not results:
            return False

        for result in results:
            fold_change = result.get('log2_fold_change', None)
            if fold_change is not None and fold_change != 0:
                return True

        return False

    def _check_pathway_results(self, data: Dict) -> bool:
        """Check for pathway analysis results"""
        pathways = data.get('pathways', [])
        return len(pathways) > 0

    def _check_self_generated_scores(self, data: Dict) -> bool:
        """Check for BANNED self-generated scores"""
        banned_keys = ['confidence_score', 'novelty_score', 'internal_validation']

        for key in banned_keys:
            if key in data:
                return True

        return False

    def _check_template_text(self, data: Dict) -> bool:
        """Check for template text indicators"""
        discovery_text = data.get('discovery', '')

        template_indicators = [
            'Dataset contains X samples',
            'Statistical power sufficient to detect',
            'This analysis provides quantitative insights into'
        ]

        for indicator in template_indicators:
            if indicator in discovery_text:
                return True

        return False

    def get_validation_statistics(self) -> Dict:
        """Get validation statistics"""

        return {
            'validations_completed': self.validations_completed,
            'validations_rejected': self.validations_rejected,
            'validations_approved': self.validations_approved,
            'approval_rate': (
                self.validations_approved / self.validations_completed
                if self.validations_completed > 0 else 0
            )
        }


def create_external_validation_system() -> ExternalValidationSystem:
    """Factory function to create external validation system"""
    return ExternalValidationSystem()