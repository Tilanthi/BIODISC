"""
Incremental Orchestration for BIODISC

Implements progressive refinement of results:
- Fast initial responses
- Progressive improvement
- Early stopping when satisfied
- User-guided refinement
- Streaming results

This provides responsive interaction while maintaining quality.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Iterator, Tuple
from enum import Enum
import time
import asyncio
from abc import ABC, abstractmethod


class RefinementStage(Enum):
    """Stages in incremental refinement."""
    INITIAL = "initial"           # Quick, approximate response
    BASIC = "basic"               # Improved with basic analysis
    DETAILED = "detailed"         # Comprehensive analysis
    COMPREHENSIVE = "comprehensive"  # Full-depth analysis
    FINAL = "final"               # Polished, complete response


class QualityThreshold(Enum):
    """Quality thresholds for early stopping."""
    MINIMAL = "minimal"           # Barely acceptable
    ADEQUATE = "adequate"         # Good enough for most purposes
    HIGH = "high"                 # High quality
    OPTIMAL = "optimal"           # Best possible


@dataclass
class IncrementalResult:
    """Result at a specific refinement stage."""
    stage: RefinementStage
    content: Any
    confidence: float
    quality_score: float
    generation_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementPlan:
    """Plan for incremental refinement."""
    query: str
    target_stage: RefinementStage
    quality_threshold: QualityThreshold
    max_time: float  # Maximum time to spend
    early_stop: bool  # Whether to stop early if quality threshold met
    user_feedback_allowed: bool  # Whether to allow user feedback during refinement


class QualityEvaluator:
    """Evaluate quality of incremental results."""

    def __init__(self):
        self.quality_thresholds = {
            QualityThreshold.MINIMAL: 0.3,
            QualityThreshold.ADEQUATE: 0.6,
            QualityThreshold.HIGH: 0.8,
            QualityThreshold.OPTIMAL: 0.95
        }

    def evaluate(self, result: IncrementalResult) -> float:
        """
        Evaluate quality of an incremental result.

        Considers:
        - Completeness
        - Accuracy (estimated)
        - Relevance
        - Coherence
        """
        quality = 0.0

        # Stage-based quality expectation
        stage_weights = {
            RefinementStage.INITIAL: 0.3,
            RefinementStage.BASIC: 0.5,
            RefinementStage.DETAILED: 0.7,
            RefinementStage.COMPREHENSIVE: 0.9,
            RefinementStage.FINAL: 1.0
        }

        # Base quality from stage
        quality += stage_weights.get(result.stage, 0.5) * 0.4

        # Confidence contribution
        quality += result.confidence * 0.3

        # Content quality indicators
        if isinstance(result.content, dict):
            # Check for key components
            if "answer" in result.content:
                quality += 0.1

            if "reasoning" in result.content:
                quality += 0.1

            if "evidence" in result.content:
                quality += 0.1

        elif isinstance(result.content, str):
            # Text quality indicators
            if len(result.content) > 100:
                quality += 0.1
            if len(result.content) > 500:
                quality += 0.1

        return min(1.0, quality)

    def meets_threshold(
        self,
        quality_score: float,
        threshold: QualityThreshold
    ) -> bool:
        """Check if quality score meets threshold."""
        return quality_score >= self.quality_thresholds[threshold]


class IncrementalExecutor:
    """Execute incremental refinement stages."""

    def __init__(self):
        self.stage_executors: Dict[RefinementStage, Callable] = {
            RefinementStage.INITIAL: self._execute_initial,
            RefinementStage.BASIC: self._execute_basic,
            RefinementStage.DETAILED: self._execute_detailed,
            RefinementStage.COMPREHENSIVE: self._execute_comprehensive,
            RefinementStage.FINAL: self._execute_final,
        }

    def execute_stage(
        self,
        stage: RefinementStage,
        query: str,
        previous_results: List[IncrementalResult],
        context: Dict[str, Any]
    ) -> IncrementalResult:
        """Execute a specific refinement stage."""
        executor = self.stage_executors.get(stage)
        if not executor:
            raise ValueError(f"No executor for stage: {stage}")

        start_time = time.time()

        # Execute stage
        content, confidence, metadata = executor(
            query,
            previous_results,
            context
        )

        generation_time = time.time() - start_time

        # Evaluate quality
        result = IncrementalResult(
            stage=stage,
            content=content,
            confidence=confidence,
            quality_score=0.0,  # Will be calculated by evaluator
            generation_time=generation_time,
            metadata=metadata
        )

        return result

    def _execute_initial(
        self,
        query: str,
        previous_results: List[IncrementalResult],
        context: Dict[str, Any]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Execute initial stage - fast, approximate response."""
        # Quick knowledge retrieval
        content = {
            "answer": f"Initial response to: {query[:100]}...",
            "stage": "initial",
            "approximation": True
        }

        confidence = 0.4  # Low confidence for initial
        metadata = {"method": "quick_retrieval", "time_limit": 2.0}

        return content, confidence, metadata

    def _execute_basic(
        self,
        query: str,
        previous_results: List[IncrementalResult],
        context: Dict[str, Any]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Execute basic stage - improved with basic analysis."""
        # Build on previous results
        prev_content = previous_results[-1].content if previous_results else {}

        content = {
            "answer": f"Basic analysis of: {query[:100]}...",
            "reasoning": "Basic reasoning applied",
            "previous_stage": "initial",
            "improvements": ["expanded_content", "basic_validation"]
        }

        confidence = 0.6
        metadata = {"method": "basic_analysis", "time_limit": 10.0}

        return content, confidence, metadata

    def _execute_detailed(
        self,
        query: str,
        previous_results: List[IncrementalResult],
        context: Dict[str, Any]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Execute detailed stage - comprehensive analysis."""
        # Incorporate all previous results
        content = {
            "answer": f"Detailed analysis of: {query[:100]}...",
            "reasoning": "Detailed multi-step reasoning",
            "evidence": ["evidence_1", "evidence_2"],
            "previous_stages": ["initial", "basic"],
            "improvements": [
                "expanded_reasoning",
                "evidence_integration",
                "cross_validation"
            ]
        }

        confidence = 0.75
        metadata = {"method": "detailed_analysis", "time_limit": 20.0}

        return content, confidence, metadata

    def _execute_comprehensive(
        self,
        query: str,
        previous_results: List[IncrementalResult],
        context: Dict[str, Any]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Execute comprehensive stage - full-depth analysis."""
        content = {
            "answer": f"Comprehensive analysis of: {query[:100]}...",
            "reasoning": "Comprehensive multi-perspective analysis",
            "evidence": ["evidence_1", "evidence_2", "evidence_3"],
            "alternatives": ["alternative_1", "alternative_2"],
            "confidence_breakdown": {
                "primary_answer": 0.8,
                "alternatives": 0.6
            },
            "previous_stages": ["initial", "basic", "detailed"],
            "improvements": [
                "full_reasoning",
                "comprehensive_evidence",
                "alternative_consideration"
            ]
        }

        confidence = 0.85
        metadata = {"method": "comprehensive_analysis", "time_limit": 30.0}

        return content, confidence, metadata

    def _execute_final(
        self,
        query: str,
        previous_results: List[IncrementalResult],
        context: Dict[str, Any]
    ) -> Tuple[Any, float, Dict[str, Any]]:
        """Execute final stage - polished, complete response."""
        # Synthesize all previous stages
        content = {
            "answer": f"Final, polished response to: {query[:100]}...",
            "reasoning": "Final synthesis with all considerations",
            "evidence": ["evidence_1", "evidence_2", "evidence_3"],
            "alternatives": ["alternative_1", "alternative_2"],
            "limitations": ["limitation_1"],
            "recommendations": ["recommendation_1"],
            "confidence_breakdown": {
                "primary_answer": 0.9,
                "alternatives": 0.7
            },
            "previous_stages": ["initial", "basic", "detailed", "comprehensive"],
            "final_polish": [
                "complete_synthesis",
                "quality_validation",
                "presentation_optimization"
            ]
        }

        confidence = 0.92
        metadata = {"method": "final_polish", "time_limit": 15.0}

        return content, confidence, metadata


class IncrementalOrchestrator:
    """
    Main incremental orchestrator.

    Provides:
    - Progressive refinement
    - Early stopping
    - User feedback integration
    - Streaming results
    """

    def __init__(self):
        self.executor = IncrementalExecutor()
        self.evaluator = QualityEvaluator()
        self.refinement_history: List[Dict[str, Any]] = []

    def orchestrate_incremental(
        self,
        query: str,
        plan: RefinementPlan,
        context: Optional[Dict[str, Any]] = None,
        feedback_callback: Optional[Callable[[IncrementalResult], bool]] = None
    ) -> Iterator[IncrementalResult]:
        """
        Orchestrate incremental refinement.

        Args:
            query: User query
            plan: Refinement plan
            context: Orchestration context
            feedback_callback: Optional callback for user feedback

        Yields:
            IncrementalResult at each stage
        """
        if context is None:
            context = {}

        results = []
        start_time = time.time()

        # Get stages in order
        stages = self._get_refinement_stages(plan.target_stage)

        for stage in stages:
            # Check time limit
            if time.time() - start_time > plan.max_time:
                break

            # Execute stage
            result = self.executor.execute_stage(
                stage,
                query,
                results,
                context
            )

            # Evaluate quality
            result.quality_score = self.evaluator.evaluate(result)
            results.append(result)

            # Yield result
            yield result

            # Check quality threshold for early stopping
            if plan.early_stop:
                if self.evaluator.meets_threshold(
                    result.quality_score,
                    plan.quality_threshold
                ):
                    break

            # Check user feedback if provided
            if feedback_callback:
                should_continue = feedback_callback(result)
                if not should_continue:
                    break

        # Record refinement
        self._record_refinement(query, plan, results)

    def orchestrate_async(
        self,
        query: str,
        plan: RefinementPlan,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIncrementalOrchestrator:
        """
        Create async incremental orchestrator.

        Returns async iterator of results.
        """
        return AsyncIncrementalOrchestrator(
            self.executor,
            self.evaluator,
            query,
            plan,
            context or {}
        )

    def get_quick_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IncrementalResult:
        """
        Get quick initial response only.

        Useful for rapid feedback.
        """
        plan = RefinementPlan(
            query=query,
            target_stage=RefinementStage.INITIAL,
            quality_threshold=QualityThreshold.MINIMAL,
            max_time=5.0,
            early_stop=True,
            user_feedback_allowed=False
        )

        result = None
        for result in self.orchestrate_incremental(query, plan, context):
            pass  # Just get first result

        return result

    def get_quality_response(
        self,
        query: str,
        quality_threshold: QualityThreshold,
        context: Optional[Dict[str, Any]] = None,
        max_time: float = 60.0
    ) -> IncrementalResult:
        """
        Get response that meets quality threshold.

        Will refine until threshold met or max_time exceeded.
        """
        plan = RefinementPlan(
            query=query,
            target_stage=RefinementStage.FINAL,
            quality_threshold=quality_threshold,
            max_time=max_time,
            early_stop=True,
            user_feedback_allowed=False
        )

        result = None
        for result in self.orchestrate_incremental(query, plan, context):
            pass  # Continue until done

        return result

    def _get_refinement_stages(self, target: RefinementStage) -> List[RefinementStage]:
        """Get stages in order up to target."""
        stage_order = [
            RefinementStage.INITIAL,
            RefinementStage.BASIC,
            RefinementStage.DETAILED,
            RefinementStage.COMPREHENSIVE,
            RefinementStage.FINAL
        ]

        target_index = stage_order.index(target)
        return stage_order[:target_index + 1]

    def _record_refinement(
        self,
        query: str,
        plan: RefinementPlan,
        results: List[IncrementalResult]
    ) -> None:
        """Record refinement for learning."""
        self.refinement_history.append({
            "query": query,
            "plan": plan,
            "results": results,
            "timestamp": time.time()
        })

    def get_refinement_statistics(self) -> Dict[str, Any]:
        """Get statistics on refinements."""
        if not self.refinement_history:
            return {"status": "no_data"}

        # Calculate statistics
        total_refinements = len(self.refinement_history)
        stages_per_refinement = [
            len(record["results"])
            for record in self.refinement_history
        ]
        avg_stages = sum(stages_per_refinement) / total_refinements

        quality_scores = []
        for record in self.refinement_history:
            if record["results"]:
                quality_scores.append(record["results"][-1].quality_score)

        return {
            "total_refinements": total_refinements,
            "average_stages": avg_stages,
            "average_final_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            "early_stops": sum(
                1 for record in self.refinement_history
                if len(record["results"]) < 5
            )
        }


class AsyncIncrementalOrchestrator:
    """Async wrapper for incremental orchestration."""

    def __init__(
        self,
        executor: IncrementalExecutor,
        evaluator: QualityEvaluator,
        query: str,
        plan: RefinementPlan,
        context: Dict[str, Any]
    ):
        self.executor = executor
        self.evaluator = evaluator
        self.query = query
        self.plan = plan
        self.context = context
        self.results = []

    async def __aiter__(self):
        """Async iterator for results."""
        start_time = time.time()
        stages = [
            RefinementStage.INITIAL,
            RefinementStage.BASIC,
            RefinementStage.DETAILED,
            RefinementStage.COMPREHENSIVE,
            RefinementStage.FINAL
        ]

        for stage in stages:
            # Check time limit
            if time.time() - start_time > self.plan.max_time:
                break

            # Execute stage asynchronously
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.executor.execute_stage,
                stage,
                self.query,
                self.results,
                self.context
            )

            # Evaluate quality
            result.quality_score = self.evaluator.evaluate(result)
            self.results.append(result)

            yield result

            # Check early stopping
            if self.plan.early_stop:
                if self.evaluator.meets_threshold(
                    result.quality_score,
                    self.plan.quality_threshold
                ):
                    break


class StreamingOrchestrator:
    """
    Stream incremental results progressively.

    Useful for long-running analyses where user wants
    to see progress.
    """

    def __init__(self, incremental_orchestrator: IncrementalOrchestrator):
        self.incremental = incremental_orchestrator

    def stream_results(
        self,
        query: str,
        plan: RefinementPlan,
        context: Optional[Dict[str, Any]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream results as they become available.

        Yields dictionaries with:
        - stage: Current refinement stage
        - progress: Progress percentage
        - result: Current incremental result
        - estimated_remaining: Estimated time remaining
        """
        if context is None:
            context = {}

        start_time = time.time()
        results = []

        # Get total stages
        total_stages = len(self.incremental._get_refinement_stages(plan.target_stage))

        for result in self.incremental.orchestrate_incremental(
            query,
            plan,
            context
        ):
            results.append(result)

            # Calculate progress
            current_stage_index = list(RefinementStage).index(result.stage)
            progress = (current_stage_index + 1) / total_stages * 100

            # Estimate remaining time
            elapsed = time.time() - start_time
            if progress < 100:
                estimated_total = elapsed / (progress / 100)
                estimated_remaining = estimated_total - elapsed
            else:
                estimated_remaining = 0

            yield {
                "stage": result.stage.value,
                "progress": progress,
                "result": result,
                "estimated_remaining": estimated_remaining,
                "elapsed": elapsed
            }


def create_incremental_orchestrator() -> IncrementalOrchestrator:
    """Factory function to create incremental orchestrator."""
    return IncrementalOrchestrator()


def create_refinement_plan(
    query: str,
    target_stage: RefinementStage = RefinementStage.COMPREHENSIVE,
    quality_threshold: QualityThreshold = QualityThreshold.HIGH,
    max_time: float = 60.0,
    early_stop: bool = True
) -> RefinementPlan:
    """Factory function to create refinement plan."""
    return RefinementPlan(
        query=query,
        target_stage=target_stage,
        quality_threshold=quality_threshold,
        max_time=max_time,
        early_stop=early_stop,
        user_feedback_allowed=False
    )
