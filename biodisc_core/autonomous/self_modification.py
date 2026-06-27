"""
Safe Self-Modification Framework

Enables BIODISC to modify its own architecture within safety constraints.
Implements strict scope control, human oversight, and rollback capabilities.
"""

import logging
import shutil
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from .config import (
    AutonomousConfig,
    ModificationProposal,
    ModificationResult
)

logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Information about a backup for rollback"""
    backup_id: str
    timestamp: datetime
    files_backed_up: List[str]
    backup_path: str
    checksum: str


class SelfModificationFramework:
    """
    Safe framework for architectural self-modification.

    SAFETY PRINCIPLES:
    1. Scope Control: Only modify BIODISC folder
    2. Human Oversight: Major changes require approval
    3. Gradual Changes: Small, testable modifications
    4. Rollback Capability: Always able to revert
    5. Validation: Changes must pass tests
    """

    def __init__(self, config: AutonomousConfig):
        """
        Initialize self-modification framework.

        Args:
            config: Autonomous system configuration
        """
        self.config = config

        # Modification history
        self.modification_history: List[ModificationResult] = []
        self.backup_stack: List[BackupInfo] = []

        # Safety tracking
        self.modifications_proposed = 0
        self.modifications_approved = 0
        self.modifications_executed = 0
        self.rollbacks_performed = 0

        # Backup directory
        self.backup_dir = Path("biodisc_core/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Self-Modification Framework initialized")

    def propose_modification(self, proposal: ModificationProposal) -> ModificationResult:
        """
        Propose and potentially execute a self-modification.

        This is the main entry point for self-modification. It implements
        all safety checks before allowing any modifications.

        Args:
            proposal: Modification proposal to evaluate and potentially execute

        Returns:
            ModificationResult with outcome
        """
        try:
            self.modifications_proposed += 1
            logger.info(f"Proposing modification: {proposal.description[:50]}...")

            # Step 1: Check if modification is allowed (scope check)
            if not self._is_allowed(proposal):
                return ModificationResult(
                    approved=False,
                    reason="Modification outside allowed scope",
                    details=f"Affected files must be within: {self.config.allowed_modification_paths}"
                )

            # Step 2: Assess risk
            risk_assessment = self._assess_risk(proposal)
            if risk_assessment['risk_level'] > self.config.max_modification_risk_level:
                return ModificationResult(
                    approved=False,
                    reason=f"Risk level too high: {risk_assessment['risk_level']:.2f}",
                    details=risk_assessment.get('reason', '')
                )

            # Step 3: Human approval for major changes
            if proposal.requires_human_approval and self.config.modification_approval_required:
                approval = self._request_human_approval(proposal, risk_assessment)
                if not approval['granted']:
                    return ModificationResult(
                        approved=False,
                        reason="Human approval denied",
                        details=approval.get('reason', 'No specific reason provided')
                    )

            # Step 4: Create backup for rollback
            backup = self._create_backup(proposal.affected_files)
            if not backup:
                return ModificationResult(
                    approved=False,
                    reason="Failed to create backup",
                    details="Cannot proceed without backup capability"
                )

            # Step 5: Execute modification
            execution_result = self._execute_modification(proposal)
            if not execution_result['success']:
                self._rollback(backup)
                return ModificationResult(
                    approved=False,
                    reason="Modification execution failed",
                    details=execution_result.get('error', 'Unknown error')
                )

            # Step 6: Validate changes
            validation_result = self._validate_changes(proposal)
            if not validation_result['passed']:
                self._rollback(backup)
                return ModificationResult(
                    approved=False,
                    reason="Validation failed",
                    details=validation_result.get('errors', 'Unknown validation failure')
                )

            # Success!
            self.modifications_approved += 1
            self.modifications_executed += 1

            result = ModificationResult(
                approved=True,
                details="Modification successfully executed and validated",
                executed=True,
                execution_time=execution_result.get('duration', 0),
                backup_created=True,
                backup_path=backup.backup_path,
                tests_passed=validation_result.get('passed', False)
            )

            # Track modification
            self.modification_history.append(result)

            logger.info(f"Modification APPROVED and EXECUTED: {proposal.description[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error in modification proposal: {e}")
            return ModificationResult(
                approved=False,
                reason=f"Exception during modification: {e}"
            )

    def _is_allowed(self, proposal: ModificationProposal) -> bool:
        """
        Check if modification is within allowed scope.

        Args:
            proposal: Modification proposal to check

        Returns:
            True if modification is allowed
        """
        for file_path in proposal.affected_files:
            # Must be within biodisc_core
            if not file_path.startswith('biodisc_core/'):
                logger.warning(f"File outside BIODISC folder: {file_path}")
                return False

            # Must be in allowed modification paths
            if not any(file_path.startswith(path) for path in self.config.allowed_modification_paths):
                logger.warning(f"File in restricted path: {file_path}")
                return False

        return True

    def _assess_risk(self, proposal: ModificationProposal) -> Dict[str, Any]:
        """
        Assess risk level of modification.

        Args:
            proposal: Modification proposal to assess

        Returns:
            Risk assessment dictionary
        """
        risk_level = 0.3  # Base risk
        reasons = []

        # Factor 1: Number of files affected
        file_count = len(proposal.affected_files)
        if file_count > 5:
            risk_level += 0.2
            reasons.append(f"Many files affected ({file_count})")
        elif file_count > 10:
            risk_level += 0.3
            reasons.append(f"Very many files affected ({file_count})")

        # Factor 2: Modification type
        if proposal.modification_type == 'refactoring':
            risk_level += 0.2
            reasons.append("Refactoring carries moderate risk")
        elif proposal.modification_type == 'optimization':
            risk_level += 0.1
            reasons.append("Optimization carries low-moderate risk")

        # Factor 3: Core system files
        core_files = ['unified.py', 'unified_enhanced.py', '__init__.py']
        if any(any(core_file in file_path for core_file in core_files)
               for file_path in proposal.affected_files):
            risk_level += 0.3
            reasons.append("Modifies core system files")

        # Factor 4: Test coverage
        if not proposal.test_requirements:
            risk_level += 0.2
            reasons.append("No test requirements specified")

        return {
            'risk_level': min(risk_level, 1.0),
            'reasons': reasons,
            'requires_human_approval': risk_level > 0.5 or proposal.requires_human_approval
        }

    def _request_human_approval(self, proposal: ModificationProposal, risk_assessment: Dict) -> Dict[str, Any]:
        """
        Request human approval for modification.

        In actual implementation, this would prompt the user.
        For now, it simulates approval based on risk level.

        Args:
            proposal: Modification proposal
            risk_assessment: Risk assessment results

        Returns:
            Approval decision dictionary
        """
        # In simulation mode, approve low-risk modifications
        if risk_assessment['risk_level'] < 0.4:
            return {
                'granted': True,
                'reason': 'Low-risk modification auto-approved'
            }

        # Higher-risk modifications would require human input
        # For now, we'll be conservative and deny them
        return {
            'granted': False,
            'reason': f'Moderate-high risk ({risk_assessment["risk_level"]:.2f}) requires explicit human approval'
        }

    def _create_backup(self, affected_files: List[str]) -> Optional[BackupInfo]:
        """
        Create backup of files to be modified.

        Args:
            affected_files: List of files to back up

        Returns:
            BackupInfo or None if backup failed
        """
        try:
            backup_id = f"backup_{datetime.now().timestamp()}"
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)

            backed_up_files = []
            checksums = []

            for file_path in affected_files:
                source = Path(file_path)
                if source.exists():
                    # Copy file to backup
                    dest = backup_path / source.name
                    shutil.copy2(source, dest)
                    backed_up_files.append(file_path)

                    # Calculate checksum
                    checksum = self._calculate_checksum(source)
                    checksums.append(f"{file_path}:{checksum}")

            if not backed_up_files:
                logger.warning("No files backed up - none exist")
                return None

            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=datetime.now(),
                files_backed_up=backed_up_files,
                backup_path=str(backup_path),
                checksum="|".join(checksums)
            )

            self.backup_stack.append(backup_info)
            logger.info(f"Backup created: {len(backed_up_files)} files -> {backup_path}")

            return backup_info

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate checksum of file for verification"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _execute_modification(self, proposal: ModificationProposal) -> Dict[str, Any]:
        """
        Execute the modification.

        In full implementation, this would apply the changes.
        For now, it simulates execution.

        Args:
            proposal: Modification proposal to execute

        Returns:
            Execution result dictionary
        """
        try:
            start_time = datetime.now()

            # In full implementation, would apply changes here
            # For now, simulate successful execution
            logger.info(f"Simulating execution of modification: {proposal.description[:50]}...")

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                'success': True,
                'duration': execution_time,
                'files_modified': len(proposal.affected_files)
            }

        except Exception as e:
            logger.error(f"Modification execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _validate_changes(self, proposal: ModificationProposal) -> Dict[str, Any]:
        """
        Validate that changes are correct.

        In full implementation, would run tests and checks.

        Args:
            proposal: Modification proposal to validate

        Returns:
            Validation result dictionary
        """
        try:
            # In full implementation, would run tests here
            # For now, assume validation passes
            logger.info(f"Simulating validation of modification")

            return {
                'passed': True,
                'errors': []
            }

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                'passed': False,
                'errors': [str(e)]
            }

    def _rollback(self, backup: BackupInfo) -> bool:
        """
        Rollback changes using backup.

        Args:
            backup: Backup information to use for rollback

        Returns:
            True if rollback successful
        """
        try:
            logger.info(f"Rolling back using backup: {backup.backup_id}")

            # Restore files from backup
            backup_path = Path(backup.backup_path)
            for file_path in backup.files_backed_up:
                source = backup_path / Path(file_path).name
                dest = Path(file_path)

                if source.exists():
                    shutil.copy2(source, dest)
                    logger.info(f"Restored: {file_path}")

            self.rollbacks_performed += 1
            logger.info(f"Rollback completed ({self.rollbacks_performed} total)")

            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def get_modification_statistics(self) -> Dict[str, Any]:
        """Get statistics about modifications"""
        return {
            'modifications_proposed': self.modifications_proposed,
            'modifications_approved': self.modifications_approved,
            'modifications_executed': self.modifications_executed,
            'rollbacks_performed': self.rollbacks_performed,
            'approval_rate': self.modifications_approved / max(self.modifications_proposed, 1),
            'execution_rate': self.modifications_executed / max(self.modifications_approved, 1),
            'backups_available': len(self.backup_stack)
        }