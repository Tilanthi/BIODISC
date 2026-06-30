"""
V78 Task Outcome Analytics - Track task success/failure and capability usage

Monitors which capabilities are used for which tasks, success rates,
time to completion, and user satisfaction to enable correlation analysis.

Date: 2026-05-09
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import hashlib


@dataclass
class TaskRecord:
    """Record of a completed task"""
    task_id: str
    task_type: str  # "causal_analysis", "literature_review", "hypothesis_generation", etc.
    capabilities_used: List[str]  # Which V7X capabilities were deployed
    user_query: str
    system_response: str
    success: bool  # Whether task was completed successfully
    user_satisfaction: Optional[float]  # 0-1, if user provided feedback
    time_to_complete: float  # seconds
    tokens_used: int
    error_message: Optional[str] = None
    capabilities_failed: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class CapabilityPerformance:
    """Performance metrics for a capability"""
    capability_name: str
    tasks_attempted: int = 0
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    avg_time_to_completion: float = 0.0
    user_satisfaction_avg: float = 0.0
    common_success_contexts: List[str] = field(default_factory=list)
    common_failure_contexts: List[str] = field(default_factory=list)
    success_rate: float = 0.0


class TaskOutcomeAnalytics:
    """
    Tracks and analyzes task outcomes for capability optimization.

    TRACKS:
    - Which capabilities are used for which tasks
    - Success/failure rates per capability
    - Time to completion per capability combination
    - User satisfaction scores
    - Common failure modes

    ENABLES:
    - Correlation analysis: capability → outcome
    - Optimization: which capabilities work best for which tasks
    - Detection: underperforming capabilities
    """

    def __init__(self):
        self.tasks: List[TaskRecord] = []
        self.capability_performance: Dict[str, CapabilityPerformance] = {}

        # Load historical data
        self._load_historical_data()

    def _load_historical_data(self):
        """Load historical task data"""
        try:
            history_path = "/Users/gjw255/.biodisc_persistent/task_history.jsonl"
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            task_dict = json.loads(line)
                            task = TaskRecord(**task_dict)
                            self.tasks.append(task)
                            self._update_capability_performance(task)

            # Compute performance metrics
            self._compute_performance_metrics()

        except Exception as e:
            print(f"Error loading historical data: {e}")

    def record_task(self, task: TaskRecord):
        """Record a completed task"""
        self.tasks.append(task)
        self._update_capability_performance(task)
        self._save_task_history()

    def _update_capability_performance(self, task: TaskRecord):
        """Update capability performance metrics based on task"""
        for cap in task.capabilities_used:
            if cap not in self.capability_performance:
                self.capability_performance[cap] = CapabilityPerformance(capability_name=cap)

            perf = self.capability_performance[cap]
            perf.tasks_attempted += 1

            if task.success:
                perf.tasks_succeeded += 1
                # Add to success contexts
                context_key = self._get_context_key(task)
                if context_key not in perf.common_success_contexts:
                    perf.common_success_contexts.append(context_key)
            else:
                perf.tasks_failed += 1
                perf.capabilities_failed.extend(task.capabilities_failed)

            # Update satisfaction average
            if task.user_satisfaction is not None:
                n = perf.tasks_attempted
                perf.user_satisfaction_avg = (
                    (perf.user_satisfaction_avg * (n - 1) + task.user_satisfaction) / n
                )

            # Update time average
            perf.avg_time_to_completion = (
                (perf.avg_time_to_completion * (n - 1) + task.time_to_complete) / n
            )

    def _get_context_key(self, task: TaskRecord) -> str:
        """Generate context key from task"""
        # Simplified - would extract meaningful context
        if "biology" in task.user_query.lower():
            return "biology_query"
        elif "causal" in task.user_query.lower():
            return "causal_analysis"
        elif "code" in task.user_query.lower():
            return "code_generation"
        else:
            return "general"

    def _compute_performance_metrics(self):
        """Compute performance metrics for all capabilities"""
        for cap_name, perf in self.capability_performance.items():
            if perf.tasks_attempted > 0:
                perf.success_rate = perf.tasks_succeeded / perf.tasks_attempted

    def get_capability_performance(self, capability_name: str) -> Optional[CapabilityPerformance]:
        """Get performance metrics for a specific capability"""
        return self.capability_performance.get(capability_name)

    def get_all_capability_performance(self) -> Dict[str, CapabilityPerformance]:
        """Get performance metrics for all capabilities"""
        return self.capability_performance

    def get_task_success_rate(self, task_type: Optional[str] = None) -> float:
        """Get overall task success rate, optionally filtered by task type"""
        relevant_tasks = self.tasks
        if task_type:
            relevant_tasks = [t for t in self.tasks if t.task_type == task_type]

        if not relevant_tasks:
            return 0.0

        return sum(1 for t in relevant_tasks if t.success) / len(relevant_tasks)

    def analyze_capability_synergy(self) -> List[Dict[str, Any]]:
        """
        Analyze which capability combinations work well together.

        RETURNS: List of capability combinations with high success rates
        """
        # Find combinations of 2+ capabilities used together
        combo_stats = {}

        for task in self.tasks:
            if task.success and len(task.capabilities_used) >= 2:
                combo = tuple(sorted(task.capabilities_used))
                if combo not in combo_stats:
                    combo_stats[combo] = {"success": 0, "total": 0, "task_types": []}
                combo_stats[combo]["success"] += 1
                combo_stats[combo]["total"] += 1
                combo_stats[combo]["task_types"].append(task.task_type)

        # Find high-performing combinations
        synergies = []
        for combo, stats in combo_stats.items():
            if stats["total"] >= 3:  # Minimum occurrences
                success_rate = stats["success"] / stats["total"]
                if success_rate >= 0.8:  # 80%+ success rate
                    synergies.append({
                        "capabilities": list(combo),
                        "success_rate": success_rate,
                        "occurrences": stats["total"],
                        "task_types": stats["task_types"]
                    })

        # Sort by success rate
        synergies.sort(key=lambda x: x["success_rate"], reverse=True)
        return synergies

    def detect_underperforming_capabilities(self, min_tasks: int = 5, max_failure_rate: float = 0.4) -> List[str]:
        """
        Detect capabilities that are underperforming.

        ARGS:
            min_tasks: Minimum tasks attempted to be considered
            max_failure_rate: Maximum acceptable failure rate

        RETURNS: List of underperforming capability names
        """
        underperforming = []

        for cap_name, perf in self.capability_performance.items():
            if perf.tasks_attempted >= min_tasks:
                failure_rate = perf.tasks_failed / perf.tasks_attempted
                if failure_rate > max_failure_rate:
                    underperforming.append({
                        "capability": cap_name,
                        "tasks_attempted": perf.tasks_attempted,
                        "tasks_failed": perf.tasks_failed,
                        "failure_rate": failure_rate,
                        "common_failure_contexts": perf.common_failure_contexts
                    })

        return underperforming

    def get_optimal_capabilities_for_task(self, task_query: str, task_type: str) -> List[str]:
        """
        Recommend optimal capabilities for a given task.

        BASED ON:
        - Historical success rates for similar tasks
        - Capability synergy analysis
        - User satisfaction scores

        RETURNS: List of recommended capability names
        """
        # Analyze query to extract keywords
        keywords = self._extract_keywords(task_query)

        # Find successful similar tasks
        similar_tasks = [
            t for t in self.tasks
            if t.task_type == task_type and t.success
            and any(kw in t.user_query.lower() for kw in keywords)
        ]

        # Count capability usage in successful similar tasks
        capability_counts = {}
        for task in similar_tasks:
            for cap in task.capabilities_used:
                capability_counts[cap] = capability_counts.get(cap, 0) + 1

        # Sort by frequency
        recommended = sorted(capability_counts.items(), key=lambda x: x[1], reverse=True)

        return [cap for cap, count in recommended[:5]]

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query"""
        # Simplified keyword extraction
        keywords = []

        # Biology terms
        biology_terms = ["protein", "dna", "rna", "gene", "cell", "bacteria", "organism",
                        "pathway", "signaling", "regulation", "expression", "metabolism"]
        keywords.extend([t for t in biology_terms if t in query.lower()])

        # Analysis types
        analysis_types = ["causal", "correlation", "mechanism", "relationship", "predict", "explain"]
        keywords.extend([t for t in analysis_types if t in query.lower()])

        return keywords

    def get_all_tasks(self, limit: int = 100) -> List[TaskRecord]:
        """Get recent task records"""
        return self.tasks[-limit:]

    def _save_task_history(self):
        """Save task history to persistent storage"""
        try:
            os.makedirs("/Users/gjw255/.biodisc_persistent", exist_ok=True)
            history_path = "/Users/gjw255/.biodisc_persistent/task_history.jsonl"

            # Save last 1000 tasks
            recent_tasks = self.tasks[-1000:]

            with open(history_path, 'w') as f:
                for task in recent_tasks:
                    # Convert to dict
                    task_dict = {
                        'task_id': task.task_id,
                        'task_type': task.task_type,
                        'capabilities_used': task.capabilities_used,
                        'user_query': task.user_query,
                        'system_response': task.system_response,
                        'success': task.success,
                        'user_satisfaction': task.user_satisfaction,
                        'time_to_complete': task.time_to_complete,
                        'tokens_used': task.tokens_used,
                        'error_message': task.error_message,
                        'capabilities_failed': task.capabilities_failed,
                        'context': task.context,
                        'timestamp': task.timestamp
                    }
                    f.write(json.dumps(task_dict) + '\n')
        except Exception as e:
            print(f"Error saving task history: {e}")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of task outcome analytics"""
        return {
            "total_tasks": len(self.tasks),
            "overall_success_rate": self.get_task_success_rate(),
            "capabilities_analyzed": len(self.capability_performance),
            "underperforming_capabilities": self.detect_underperforming_capabilities(),
            "capability_synergies": self.analyze_capability_synergy()[:5],
            "recent_performance": {
                "last_10_success_rate": self.get_task_success_rate(),
                "avg_completion_time": sum(t.time_to_complete for t in self.tasks[-10:]) / min(10, len(self.tasks)) if len(self.tasks) > 0 else 0.0
            }
        }


def create_task_outcome_analytics() -> TaskOutcomeAnalytics:
    """Factory function to create analytics system"""
    return TaskOutcomeAnalytics()


# Singleton instance
_instance = None

def get_task_outcome_analytics() -> TaskOutcomeAnalytics:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_task_outcome_analytics()
    return _instance
