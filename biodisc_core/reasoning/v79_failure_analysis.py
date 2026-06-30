"""
V79 Failure Analysis System - Systematically analyze failures to extract root causes

Analyzes failures, hallucinations, errors, and negative outcomes to extract
root causes and generate actionable improvements.

Date: 2026-05-09
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
from enum import Enum


class FailureType(Enum):
    """Types of failures"""
    HALLUCINATION = "hallucination"           # Made up information
    TIMEOUT = "timeout"                       # Took too long
    WRONG_ANSWER = "wrong_answer"             # Answer was incorrect
    CRASH = "crash"                           # System crashed
    CAPABILITY_MISSING = "capability_missing" # Missing required capability
    CIRCULAR_REASONING = "circular_reasoning" # Logical fallacy
    OVERCONFIDENCE = "overconfidence"         # Too certain, should be uncertain
    MISUNDERSTANDING = "misunderstanding"     # Misinterpreted user intent
    INEFFICIENT = "inefficient"               # Correct but inefficient


class FailureSeverity(Enum):
    """How severe is this failure?"""
    LOW = "low"             # Minor issue, doesn't affect outcome much
    MEDIUM = "medium"       # Noticeable issue, degrades quality
    HIGH = "high"           # Major issue, prevents success
    CRITICAL = "critical"   # Severe issue, loses user trust


@dataclass
class FailureRecord:
    """Record of a failure event"""
    failure_id: str
    failure_type: FailureType
    severity: FailureSeverity
    task_id: str
    task_type: str
    user_query: str
    system_response: str
    root_cause: str
    preventing_discovery: str  # What meta-discovery would prevent this?
    timestamp: float
    capabilities_used: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailurePattern:
    """A recurring pattern of failures"""
    pattern_id: str
    pattern_name: str
    failure_type: FailureType
    description: str
    occurrences: int
    affected_capabilities: List[str]
    affected_task_types: List[str]
    root_causes: List[str]
    suggested_preventions: List[str]
    priority: float  # 0-1, higher = more important to fix


class FailureAnalysisSystem:
    """
    Analyzes failures to extract root causes and prevention strategies.

    FEATURES:
    - Tracks all failure events with detailed context
    - Identifies recurring failure patterns
    - Generates actionable prevention strategies
    - Links failures to capability improvements needed
    - Prioritizes failures by impact and frequency

    OUTPUTS:
    - Failure pattern database
    - Prevention strategies for each pattern
    - Capability improvement recommendations
    - Early warning system for emerging issues
    """

    def __init__(self):
        self.failures: List[FailureRecord] = []
        self.patterns: List[FailurePattern] = []

        # Load historical failures
        self._load_failure_history()

        # Analyze for patterns
        self._analyze_patterns()

    def _load_failure_history(self):
        """Load historical failure data"""
        try:
            history_path = "/Users/gjw255/.biodisc_persistent/failure_history.jsonl"
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            failure_dict = json.loads(line)
                            failure = FailureRecord(**failure_dict)
                            self.failures.append(failure)
        except Exception as e:
            print(f"Error loading failure history: {e}")

    def record_failure(self, failure: FailureRecord):
        """Record a failure event"""
        self.failures.append(failure)
        self._save_failure_history()

        # Re-analyze patterns
        self._analyze_patterns()

    def _analyze_patterns(self):
        """Analyze failures to identify recurring patterns"""
        # Group failures by type
        failures_by_type = {}
        for failure in self.failures:
            if failure.failure_type not in failures_by_type:
                failures_by_type[failure.failure_type] = []
            failures_by_type[failure.failure_type].append(failure)

        # Identify significant patterns (5+ occurrences)
        for fail_type, failures in failures_by_type.items():
            if len(failures) >= 5:
                # Extract root causes
                root_causes = list(set(f.root_cause for f in failures))

                # Find affected capabilities
                affected_caps = set()
                for f in failures:
                    affected_caps.update(f.capabilities_used)

                # Find affected task types
                affected_task_types = list(set(f.task_type for f in failures))

                # Generate suggested preventions
                preventions = self._generate_preventions(fail_type, failures)

                # Fix syntax error - calculate hash correctly
                import hashlib
                hash_input = str(len(failures))
                hash_digest = hashlib.md5(hash_input.encode()).hexdigest()
                hash_suffix = hash_digest[:8]
                pattern_id = f"pattern_{fail_type.value}_{hash_suffix}"

                pattern = FailurePattern(
                    pattern_id=pattern_id,
                    pattern_name=f"Recurring {fail_type.value}",
                    failure_type=fail_type,
                    description=f"{fail_type.value} occurs {len(failures)} times across {len(affected_caps)} capabilities",
                    occurrences=len(failures),
                    affected_capabilities=list(affected_caps),
                    affected_task_types=affected_task_types,
                    root_causes=root_causes,
                    suggested_preventions=preventions,
                    priority=self._calculate_pattern_priority(fail_type, len(failures))
                )

                self.patterns.append(pattern)

        # Sort by priority
        self.patterns.sort(key=lambda p: p.priority, reverse=True)

    def _generate_preventions(self, fail_type: FailureType, failures: List[FailureRecord]) -> List[str]:
        """Generate prevention strategies for a failure type"""

        if fail_type == FailureType.HALLUCINATION:
            return [
                "Add unstudied_organism detection - refuse to guess",
                "Implement uncertainty quantification for low-evidence claims",
                "Cross-reference with database before making claims",
                "Add confidence calibration to predictions"
            ]

        elif fail_type == FailureType.OVERCONFIDENCE:
            return [
                "Add confidence intervals to all predictions",
                "Implement uncertainty tracking in reasoning chains",
                "Flag claims with insufficient evidence",
                "Add 'confidence too high' warning system"
            ]

        elif fail_type == FailureType.CIRCULAR_REASONING:
            return [
                "Implement causal graph validation",
                "Add circular dependency detection",
                "Require independent evidence for each causal link",
                "Add circular reasoning warning system"
            ]

        elif fail_type == FailureType.CAPABILITY_MISSING:
            # Find which capabilities are commonly needed
            needed_caps = {}
            for f in failures:
                for missing in f.capabilities_failed:
                    needed_caps[missing] = needed_caps.get(missing, 0) + 1

            return [
                f"Implement top missing capabilities: {sorted(needed_caps.items(), key=lambda x: x[1], reverse=True)[:3]}",
                "Add capability gap detection before task starts",
                "Suggest alternative approaches when capabilities missing"
            ]

        elif fail_type == FailureType.TIMEOUT:
            return [
                "Implement early timeout detection",
                "Add step-by-step progress tracking",
                "Break long tasks into sub-tasks with checkpoints",
                "Add 'taking too long' warning to user"
            ]

        elif fail_type == FailureType.MISUNDERSTANDING:
            return [
                "Implement query clarification system",
                "Add intent confirmation before proceeding",
                "Break complex queries into sub-questions",
                "Request clarification for ambiguous terms"
            ]

        else:
            return ["Investigate specific failure patterns", "Add domain-specific validation"]

    def _calculate_pattern_priority(self, fail_type: FailureType, occurrences: int) -> float:
        """Calculate priority score for a pattern"""
        # Priority based on:
        # - Severity of failure type
        # - Frequency of occurrence
        # - Impact on user trust

        severity_scores = {
            FailureType.HALLUCINATION: 0.9,
            FailureType.OVERCONFIDENCE: 0.8,
            FailureType.CIRCULAR_REASONING: 0.7,
            FailureType.CAPABILITY_MISSING: 0.6,
            FailureType.TIMEOUT: 0.4,
            FailureType.WRONG_ANSWER: 0.7,
            FailureType.CRASH: 0.95,
            FailureType.MISUNDERSTANDING: 0.5,
            FailureType.INEFFICIENT: 0.3
        }

        severity = severity_scores.get(fail_type, 0.5)
        frequency = min(1.0, occurrences / 20)  # Saturates at 20 occurrences

        return (severity * 0.7 + frequency * 0.3)

    def get_top_priority_patterns(self, limit: int = 10) -> List[FailurePattern]:
        """Get highest priority failure patterns"""
        return self.patterns[:limit]

    def get_failure_summary(self) -> Dict[str, Any]:
        """Get summary of failure analysis"""
        failures_by_type = {}
        for failure in self.failures:
            ftype = failure.failure_type.value
            if ftype not in failures_by_type:
                failures_by_type[ftype] = []
            failures_by_type[ftype].append(failure)

        return {
            "total_failures": len(self.failures),
            "failures_by_type": {k: len(v) for k, v in failures_by_type.items()},
            "identified_patterns": len(self.patterns),
            "top_patterns": [
                {
                    "pattern": p.pattern_name,
                    "occurrences": p.occurrences,
                    "priority": p.priority
                }
                for p in self.patterns[:5]
            ]
        }

    def _save_failure_history(self):
        """Save failure history to persistent storage"""
        try:
            os.makedirs("/Users/gjw255/.biodisc_persistent", exist_ok=True)
            history_path = "/Users/gjw255/.biodisc_persistent/failure_history.jsonl"

            # Save last 1000 failures
            recent_failures = self.failures[-1000:]

            with open(history_path, 'w') as f:
                for failure in recent_failures:
                    # Convert to dict
                    failure_dict = {
                        'failure_id': failure.failure_id,
                        'failure_type': failure.failure_type.value,
                        'severity': failure.severity.value,
                        'task_id': failure.task_id,
                        'task_type': failure.task_type,
                        'user_query': failure.user_query,
                        'system_response': failure.system_response,
                        'root_cause': failure.root_cause,
                        'preventing_discovery': failure.preventing_discovery,
                        'timestamp': failure.timestamp,
                        'capabilities_used': failure.capabilities_used,
                        'context': failure.context
                    }
                    f.write(json.dumps(failure_dict) + '\n')
        except Exception as e:
            print(f"Error saving failure history: {e}")


def create_failure_analysis_system() -> FailureAnalysisSystem:
    """Factory function to create failure analysis system"""
    return FailureAnalysisSystem()


# Singleton instance
_instance = None

def get_failure_analysis_system() -> FailureAnalysisSystem:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_failure_analysis_system()
    return _instance
