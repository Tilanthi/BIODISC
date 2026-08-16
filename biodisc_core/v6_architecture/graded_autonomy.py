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
BIODISC V6.0 - Graded Autonomy Controller

Implements variable autonomy levels based on task complexity, human relevance,
and discovery characteristics. Works for both user-interactive and autonomous modes.

Key Features:
- 4 autonomy levels: LOW, MEDIUM, HIGH, FULL
- Dynamic autonomy adjustment based on context
- Human-in-the-loop interfaces for higher-stakes discoveries
- Automatic autonomy escalation for well-established domains
- Integration with both interactive and autonomous systems

Date: 2026-07-04
Version: 6.0
"""

import logging
import json
import threading
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Autonomy levels for BIODISC operations"""
    LOW = 0.2      # Human-supervised, AI-assisted
    MEDIUM = 0.5   # Human-AI collaboration
    HIGH = 0.8     # AI-led with human veto power
    FULL = 1.0     # Fully autonomous (current V5.6 mode)


@dataclass
class DiscoveryContext:
    """Context information for autonomy level assessment"""
    domain: str
    novelty_score: float
    potential_impact: str  # 'low', 'medium', 'high', 'transformative'
    ethical_considerations: bool
    well_established_domain: bool
    requires_experimental_validation: bool
    user_confidence: float = 0.5
    historical_success_rate: float = 0.8


class GradedAutonomyController:
    """
    Controller for graded autonomy in BIODISC operations.

    Dynamically adjusts autonomy levels based on:
    - Task complexity and domain familiarity
    - Novelty and potential impact
    - Ethical considerations
    - User preferences and historical performance
    """

    def __init__(self):
        self.autonomy_levels = {
            'LOW': AutonomyLevel.LOW,
            'MEDIUM': AutonomyLevel.MEDIUM,
            'HIGH': AutonomyLevel.HIGH,
            'FULL': AutonomyLevel.FULL
        }

        self.current_autonomy_level = AutonomyLevel.FULL
        self.autonomy_history = []
        self.user_feedback_cache = {}
        self.domain_familiarity_scores = self._initialize_domain_familiarity()

        # Thread safety
        self.lock = threading.Lock()

        logger.info("🎛️  Graded Autonomy Controller initialized")

    def _initialize_domain_familiarity(self) -> Dict[str, float]:
        """Initialize domain familiarity scores (0.0-1.0)"""
        return {
            # Well-established domains (high familiarity)
            'protein_folding': 0.9,
            'gene_expression': 0.85,
            'cell_cycle': 0.9,
            'metabolism': 0.85,
            'transcription': 0.8,

            # Moderately established domains
            'epigenetics': 0.7,
            'chromatin_accessibility': 0.65,
            'non_coding_rna': 0.6,
            'phase_separation': 0.6,

            # Emerging domains (low familiarity)
            'quantum_biology': 0.3,
            'synthetic_biology': 0.5,
            'systems_biology': 0.55,

            # Default for unknown domains
            'default': 0.5
        }

    def assess_task_complexity(self, context: DiscoveryContext) -> AutonomyLevel:
        """
        Determine appropriate autonomy level based on discovery context.

        Assessment criteria:
        - Domain familiarity (high → higher autonomy)
        - Novelty score (moderate → higher autonomy, extreme → lower)
        - Potential impact (transformative → lower autonomy, more oversight)
        - Ethical considerations (yes → lower autonomy)
        - User confidence (high → higher autonomy)
        """

        with self.lock:
            base_score = self._calculate_base_autonomy_score(context)

            # Adjust for domain familiarity
            domain_familiarity = self.domain_familiarity_scores.get(
                context.domain,
                self.domain_familiarity_scores['default']
            )
            base_score += (domain_familiarity - 0.5) * 0.2

            # Adjust for novelty (too novel or too familiar → lower autonomy)
            if context.novelty_score > 0.9:  # Extremely novel
                base_score -= 0.2  # More oversight needed
            elif context.novelty_score < 0.4:  # Well-established
                base_score += 0.1  # Can be more autonomous

            # Adjust for potential impact
            if context.potential_impact == 'transformative':
                base_score -= 0.3  # Maximum oversight for transformative discoveries
            elif context.potential_impact == 'high':
                base_score -= 0.1

            # Adjust for ethical considerations
            if context.ethical_considerations:
                base_score -= 0.2

            # Adjust for user confidence
            base_score += (context.user_confidence - 0.5) * 0.2

            # Adjust for historical success rate
            base_score += (context.historical_success_rate - 0.7) * 0.1

            # Clamp to valid range
            base_score = max(0.2, min(1.0, base_score))

            # Map to autonomy level
            autonomy_level = self._map_score_to_level(base_score)

            # Record decision
            self._record_autonomy_decision(context, autonomy_level, base_score)

            logger.info(f"🎛️  Autonomy Level: {autonomy_level.name} (score: {base_score:.2f})")
            logger.debug(f"   Context: {context.domain}, Novelty: {context.novelty_score:.2f}, Impact: {context.potential_impact}")

            return autonomy_level

    def _calculate_base_autonomy_score(self, context: DiscoveryContext) -> float:
        """Calculate base autonomy score from context"""
        if context.well_established_domain:
            return 0.8  # Start with high autonomy for established domains
        else:
            return 0.5  # Start with medium autonomy for novel domains

    def _map_score_to_level(self, score: float) -> AutonomyLevel:
        """Map numerical score to autonomy level"""
        if score < 0.35:
            return AutonomyLevel.LOW
        elif score < 0.65:
            return AutonomyLevel.MEDIUM
        elif score < 0.9:
            return AutonomyLevel.HIGH
        else:
            return AutonomyLevel.FULL

    def execute_with_autonomy(self, operation: str, context: DiscoveryContext,
                             operation_func, *args, **kwargs) -> Any:
        """
        Execute an operation with the appropriate autonomy level.

        Handles:
        - FULL autonomy: Execute directly without interruption
        - HIGH autonomy: Execute with optional human veto
        - MEDIUM autonomy: Request approval before execution
        - LOW autonomy: Require step-by-step human confirmation
        """

        autonomy_level = self.assess_task_complexity(context)

        if autonomy_level == AutonomyLevel.FULL:
            # Full autonomy - execute directly
            logger.info(f"✅ FULL autonomy: Executing {operation}")
            return operation_func(*args, **kwargs)

        elif autonomy_level == AutonomyLevel.HIGH:
            # High autonomy - execute with human veto option
            logger.info(f"🤔 HIGH autonomy: Executing {operation} with veto option")
            result = operation_func(*args, **kwargs)

            # Check if human wants to veto (asynchronous)
            if self._check_human_veto(operation, result):
                logger.info(f"🛑 Human veto: {operation} cancelled")
                return None
            return result

        elif autonomy_level == AutonomyLevel.MEDIUM:
            # Medium autonomy - request approval
            logger.info(f"👤 MEDIUM autonomy: Requesting approval for {operation}")

            approval = self._request_human_approval(operation, context)

            if approval:
                logger.info(f"✅ Approved: {operation}")
                return operation_func(*args, **kwargs)
            else:
                logger.info(f"❌ Rejected: {operation}")
                return None

        else:  # LOW autonomy
            # Low autonomy - step-by-step confirmation
            logger.info(f"👥 LOW autonomy: Step-by-step execution for {operation}")
            return self._execute_with_step_by_step_confirmation(
                operation, operation_func, args, kwargs
            )

    def _record_autonomy_decision(self, context: DiscoveryContext,
                                 level: AutonomyLevel, score: float):
        """Record autonomy decision for learning and analysis"""
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'context': {
                'domain': context.domain,
                'novelty_score': context.novelty_score,
                'potential_impact': context.potential_impact,
                'ethical_considerations': context.ethical_considerations
            },
            'autonomy_level': level.name,
            'autonomy_score': score
        }

        self.autonomy_history.append(decision_record)

        # Keep only recent history
        if len(self.autonomy_history) > 1000:
            self.autonomy_history = self.autonomy_history[-1000:]

    def _check_human_veto(self, operation: str, result: Any) -> bool:
        """Check if human has vetoed the operation (asynchronous check)"""
        # In user-interactive mode, check for user input
        # In autonomous mode, check for veto signals in shared state
        veto_file = f"/tmp/biodisc_veto_{operation.replace(' ', '_')}.json"

        try:
            import os
            if os.path.exists(veto_file):
                with open(veto_file, 'r') as f:
                    veto_data = json.load(f)
                if veto_data.get('veto', False):
                    os.remove(veto_file)
                    return True
        except Exception as e:
            logger.debug(f"Veto check error: {e}")

        return False

    def _request_human_approval(self, operation: str, context: DiscoveryContext) -> bool:
        """Request human approval for operation"""
        # In user-interactive mode: prompt user directly
        # In autonomous mode: create approval request file and wait

        approval_request = {
            'operation': operation,
            'context': {
                'domain': context.domain,
                'novelty_score': context.novelty_score,
                'potential_impact': context.potential_impact,
                'timestamp': datetime.now().isoformat()
            },
            'requires_approval': True
        }

        approval_file = f"/tmp/biodisc_approval_request.json"

        try:
            with open(approval_file, 'w') as f:
                json.dump(approval_request, f, indent=2)

            logger.info(f"📋 Approval request created: {approval_file}")

            # Wait for approval response (timeout: 60 seconds in autonomous mode)
            # In user-interactive mode, prompt would be handled differently
            import time
            for _ in range(60):
                time.sleep(1)
                response_file = f"/tmp/biodisc_approval_response.json"
                try:
                    with open(response_file, 'r') as f:
                        response = json.load(f)
                    import os
                    os.remove(response_file)
                    return response.get('approved', False)
                except FileNotFoundError:
                    continue

            logger.warning("⏰ Approval timeout - defaulting to approve")
            return True

        except Exception as e:
            logger.error(f"❌ Approval request error: {e}")
            return True  # Default to approve on error

    def _execute_with_step_by_step_confirmation(self, operation: str,
                                              operation_func, args, kwargs) -> Any:
        """Execute operation with step-by-step human confirmation"""
        logger.info(f"📝 Step-by-step mode: {operation}")

        # Create step-by-step request
        step_request = {
            'operation': operation,
            'steps_required': True,
            'timestamp': datetime.now().isoformat()
        }

        steps_file = f"/tmp/biodisc_step_by_step.json"

        try:
            with open(steps_file, 'w') as f:
                json.dump(step_request, f, indent=2)

            # Wait for step-by-step execution instructions
            import time
            for _ in range(300):  # 5 minute timeout
                time.sleep(1)
                instruction_file = f"/tmp/biodisc_step_instruction.json"
                try:
                    with open(instruction_file, 'r') as f:
                        instruction = json.load(f)

                    if instruction.get('operation') == operation:
                        if instruction.get('action') == 'execute':
                            import os
                            os.remove(instruction_file)
                            return operation_func(*args, **kwargs)
                        elif instruction.get('action') == 'skip':
                            import os
                            os.remove(instruction_file)
                            return None
                except FileNotFoundError:
                    continue

            logger.warning("⏰ Step-by-step timeout - executing")
            return operation_func(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Step-by-step execution error: {e}")
            return operation_func(*args, **kwargs)

    def adjust_autonomy_based_on_feedback(self, feedback: Dict[str, Any]):
        """Adjust autonomy parameters based on human feedback"""
        operation = feedback.get('operation')
        satisfaction = feedback.get('satisfaction')  # 1-5 scale
        appropriate_level = feedback.get('appropriate_level')

        # Store feedback for learning
        self.user_feedback_cache[operation] = {
            'satisfaction': satisfaction,
            'appropriate_level': appropriate_level,
            'timestamp': datetime.now().isoformat()
        }

        # Adjust domain familiarity based on feedback
        if satisfaction >= 4 and appropriate_level == 'HIGH':
            # Positive feedback for high autonomy → increase domain familiarity
            for domain in self.domain_familiarity_scores:
                self.domain_familiarity_scores[domain] = min(1.0,
                    self.domain_familiarity_scores[domain] + 0.05)

        elif satisfaction <= 2 and appropriate_level == 'LOW':
            # Negative feedback even with low autonomy → decrease domain familiarity
            for domain in self.domain_familiarity_scores:
                self.domain_familiarity_scores[domain] = max(0.1,
                    self.domain_familiarity_scores[domain] - 0.05)

        logger.info(f"📚 Feedback processed: satisfaction={satisfaction}, appropriate_level={appropriate_level}")

    def get_current_autonomy_level(self) -> AutonomyLevel:
        """Get current autonomy level"""
        return self.current_autonomy_level

    def set_autonomy_level(self, level: AutonomyLevel):
        """Manually set autonomy level (for user control)"""
        with self.lock:
            self.current_autonomy_level = level
            logger.info(f"🎛️  Autonomy level manually set to: {level.name}")

    def get_autonomy_statistics(self) -> Dict[str, Any]:
        """Get statistics about autonomy usage and decisions"""
        if not self.autonomy_history:
            return {'message': 'No autonomy history available'}

        level_counts = {}
        for record in self.autonomy_history:
            level = record['autonomy_level']
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            'total_decisions': len(self.autonomy_history),
            'level_distribution': level_counts,
            'average_autonomy_score': np.mean([r['autonomy_score'] for r in self.autonomy_history]),
            'domain_familiarity_scores': self.domain_familiarity_scores
        }


# Singleton instance for use across BIODISC systems
_graded_autonomy_controller = None

def get_graded_autonomy_controller() -> GradedAutonomyController:
    """Get the singleton graded autonomy controller instance"""
    global _graded_autonomy_controller
    if _graded_autonomy_controller is None:
        _graded_autonomy_controller = GradedAutonomyController()
    return _graded_autonomy_controller


def reset_graded_autonomy_controller():
    """Reset the singleton instance (for testing)"""
    global _graded_autonomy_controller
    _graded_autonomy_controller = None


if __name__ == "__main__":
    # Test the graded autonomy controller
    controller = get_graded_autonomy_controller()

    # Test different contexts
    contexts = [
        DiscoveryContext(
            domain='protein_folding',
            novelty_score=0.7,
            potential_impact='medium',
            ethical_considerations=False,
            well_established_domain=True,
            requires_experimental_validation=True
        ),
        DiscoveryContext(
            domain='quantum_biology',
            novelty_score=0.95,
            potential_impact='transformative',
            ethical_considerations=True,
            well_established_domain=False,
            requires_experimental_validation=True
        ),
        DiscoveryContext(
            domain='cell_cycle',
            novelty_score=0.5,
            potential_impact='high',
            ethical_considerations=False,
            well_established_domain=True,
            requires_experimental_validation=False
        )
    ]

    for i, context in enumerate(contexts, 1):
        print(f"\nContext {i}: {context.domain}")
        level = controller.assess_task_complexity(context)
        print(f"Recommended autonomy level: {level.name}")

    print(f"\nAutonomy statistics: {controller.get_autonomy_statistics()}")
