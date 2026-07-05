"""
V73 WORKING Autonomous Discovery Orchestrator - FINAL SOLUTION

CRITICAL FIX: This version implements the complete solution for genuine discovery.

ROOT CAUSE IDENTIFIED:
The original routing logic was:
1. Questions with keywords like 'data', 'expression' → computational analysis ✅
2. Questions with 'how', 'why', 'mechanism' → insight generation ❌

PROBLEM: Insight generator received question metadata instead of computational results!
- It expected {'findings': '...', 'quantitative_insights': [...]}
- But got {'question': '...', 'context': '...'}
- Result: "No findings in computational results"

SOLUTION:
1. ALL questions now route through computational analysis first
2. Computational analysis generates genuine findings with statistical evidence
3. Only then does insight generation interpret the results
4. Discoveries have proper computational backing

Date: 2026-07-01
Version: 4.0 - WORKING
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import threading
from datetime import datetime, timedelta
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

# Import analysis components
try:
    from ..analysis.computational_biology import ComputationalBiologyAnalyzer, create_computational_biology_analyzer
    from ..analysis.computational_integrator import create_computational_analysis_integrator
    COMPUTATIONAL_AVAILABLE = True
except ImportError:
    COMPUTATIONAL_AVAILABLE = False

# Import curiosity engine
try:
    from .v73_curiosity_engine import get_curiosity_engine, CuriosityQuestion
    CURIOSITY_AVAILABLE = True
except ImportError:
    CURIOSITY_AVAILABLE = False


class DiscoveryStatus(Enum):
    """Status of autonomous discovery system"""
    IDLE = "idle"
    GENERATING = "generating_questions"
    EXPLORING = "exploring_question"
    ANALYZING = "performing_computational_analysis"
    VALIDATING = "validating_discovery"
    STORING = "storing_discovery"
    PAUSED = "paused"
    SLEEPING = "sleeping"


@dataclass
class Discovery:
    """Represents a genuine scientific discovery with computational backing"""
    id: str
    question: CuriosityQuestion
    discovery: str
    confidence: float
    evidence: List[str]
    timestamp: float
    validation_status: str = "pending"
    computational_backing: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkingAutonomousDiscoveryConfig:
    """Configuration for working autonomous discovery"""
    max_cpu_percent: float = 15.0
    max_hours_per_week: float = 168.0
    idle_timeout_minutes: int = 2
    min_confidence_to_store: float = 0.70
    min_evidence_count: int = 2
    bioscience_mode: bool = True
    questions_per_cycle: int = 8
    cycle_interval_seconds: int = 10
    log_all_discoveries: bool = True
    discovery_log_path: str = "autonomous_discoveries.jsonl"
    forbidden_domains: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=lambda: [
        "biology", "genetics", "molecular_biology", "cell_biology",
        "biochemistry", "biophysics", "microbiology", "evolutionary_biology"
    ])
    min_discovery_confidence: float = 0.75


class WorkingAutonomousDiscoveryOrchestrator:
    """
    WORKING autonomous discovery orchestrator with proper computational integration.

    KEY FIX: All questions now receive computational analysis before insight generation.
    """

    def __init__(self, config=None):
        self.config = config or WorkingAutonomousDiscoveryConfig()
        self.status = DiscoveryStatus.IDLE
        self.running = False
        self.paused = False
        self.discoveries = []
        self.discovery_thread = None
        self.last_activity_time = datetime.now()
        self.session_start_time = datetime.now()
        self.weekly_cpu_hours = 0.0

        # Initialize computational components
        self._initialize_components()

        logger.info("WORKING autonomous discovery orchestrator initialized")

    def _initialize_components(self):
        """Initialize computational analysis components"""
        # Initialize curiosity engine
        if CURIOSITY_AVAILABLE:
            try:
                self.curiosity_engine = get_curiosity_engine()
                logger.info("Curiosity engine initialized")
            except Exception as e:
                logger.warning(f"Could not initialize curiosity engine: {e}")
                self.curiosity_engine = None

        # Initialize computational analyzer
        if COMPUTATIONAL_AVAILABLE:
            try:
                self.computational_analyzer = create_computational_biology_analyzer()
                logger.info("Computational analyzer initialized")
            except Exception as e:
                logger.warning(f"Could not initialize computational analyzer: {e}")
                self.computational_analyzer = None
        else:
            self.computational_analyzer = None

        # Initialize computational integrator
        if self.computational_analyzer:
            try:
                self.computational_integrator = create_computational_analysis_integrator(
                    self.computational_analyzer
                )
                logger.info("✅ Computational integrator initialized")
            except Exception as e:
                logger.warning(f"Could not initialize computational integrator: {e}")
                self.computational_integrator = None
        else:
            self.computational_integrator = None

    def start(self):
        """Start autonomous discovery in background"""
        if self.running:
            return

        self.running = True
        self.paused = False
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()

    def stop(self):
        """Stop autonomous discovery"""
        self.running = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=5)

    def pause(self):
        """Pause autonomous discovery"""
        self.paused = True
        self.status = DiscoveryStatus.PAUSED

    def resume(self):
        """Resume autonomous discovery"""
        self.paused = False
        if self.status == DiscoveryStatus.PAUSED:
            self.status = DiscoveryStatus.SLEEPING

    def update_activity(self):
        """Update last activity time"""
        self.last_activity_time = datetime.now()

    def _discovery_loop(self):
        """Main discovery loop with WORKING computational integration"""
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        cycle_count = 0
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"=== WORKING Discovery cycle {cycle_count} ===")

                if self.paused:
                    logger.info("System paused, waiting...")
                    time.sleep(60)
                    continue

                if not self._within_resource_limits():
                    logger.info("Resource limit reached, pausing...")
                    self.status = DiscoveryStatus.SLEEPING
                    time.sleep(10)
                    continue

                # CRITICAL: For testing, bypass idle check to ensure discovery runs
                idle_time = (datetime.now() - self.last_activity_time).total_seconds()
                logger.info(f"Idle time: {idle_time:.1f}s (required: {self.config.idle_timeout_minutes * 60}s)")

                if not self._is_idle():
                    logger.info("System not idle, waiting...")
                    time.sleep(5)
                    continue

                logger.info("✅ System idle, starting WORKING discovery cycle")

                # Generate curiosity questions
                self.status = DiscoveryStatus.GENERATING
                logger.info("Generating curiosity questions...")
                questions = self._generate_questions()
                logger.info(f"✅ Generated {len(questions)} questions")

                if not questions:
                    logger.debug("No questions generated, retrying")
                    time.sleep(5)
                    continue

                # Explore top questions with WORKING computational integration
                self.status = DiscoveryStatus.EXPLORING
                for question in questions[:3]:
                    logger.info(f"Exploring question: {question.question[:50]}...")

                    # CRITICAL FIX: Use working exploration with computational analysis
                    discovery = self._explore_question_working(question)

                    if discovery:
                        logger.info(f"✅ Discovery created: {discovery.id}, confidence: {discovery.confidence}")

                        # Validate discovery
                        self.status = DiscoveryStatus.VALIDATING
                        validated = self._validate_discovery(discovery)

                        if validated:
                            # Store in memory
                            self.status = DiscoveryStatus.STORING
                            logger.info(f"Storing discovery {discovery.id}...")
                            self._store_discovery(discovery)
                            logger.info(f"✅ Discovery {discovery.id} stored successfully")
                        else:
                            logger.warning(f"Discovery {discovery.id} failed validation")
                    else:
                        logger.debug("No discovery created from question")

                # Sleep before next cycle
                time.sleep(self.config.cycle_interval_seconds)
                self.status = DiscoveryStatus.SLEEPING

            except Exception as e:
                logger.error(f"WORKING autonomous discovery error: {e}", exc_info=True)
                self.status = DiscoveryStatus.SLEEPING
                time.sleep(1)

    def _explore_question_working(self, question: CuriosityQuestion) -> Optional[Discovery]:
        """
        WORKING question exploration with proper computational integration.

        CRITICAL FIX: All questions now get computational analysis first.
        """
        try:
            logger.info(f"WORKING exploration: {question.question[:50]}...")

            # AUTOMATIC CONTEXT PRESERVATION - Save autonomous question
            # This provides continuity for autonomous discovery cycles
            try:
                from biodisc_core.memory.persistent.context_preservation import save_last_context
                save_last_context(
                    question=question.question,
                    response=None,  # Will be updated when discovery is made
                    metadata={
                        'current_task': f'Autonomous exploration: {question.question[:100]}',
                        'question_type': 'autonomous',
                        'active_work': 'autonomous_discovery',
                        'context_summary': f'Exploring {question.question_type.value} question'
                    }
                )
            except ImportError:
                # Context preservation module not available - silently continue
                pass
            except Exception:
                # Don't break discovery if context save fails
                pass

            if not self.computational_integrator:
                logger.error("Computational integrator not available")
                return None

            # Step 1: Perform computational analysis
            self.status = DiscoveryStatus.ANALYZING
            logger.info("Step 1: Performing computational analysis...")

            computational_result = self.computational_integrator.route_question_to_analysis(
                question.question,
                question.context or ""
            )

            if not computational_result:
                logger.warning("Computational analysis returned no results")
                return None

            logger.info(f"✅ Computational analysis completed: {computational_result.get('analysis_type', 'unknown')}")

            # Step 2: Create discovery from computational result
            discovery_text = f"Computational Analysis: {question.question}\n\n"
            discovery_text += f"Analysis Type: {computational_result['analysis_type']}\n\n"
            discovery_text += f"Findings:\n{computational_result['findings']}\n\n"
            discovery_text += f"Methodology: {computational_result['methodology']}\n\n"
            discovery_text += f"Confidence: {computational_result['confidence']:.2f}\n\n"

            # Build evidence list
            evidence = [
                f"Computational analysis: {computational_result['analysis_type']}",
                f"Methodology: {computational_result['methodology']}"
            ]

            # Add quantitative insights as evidence
            if 'quantitative_insights' in computational_result:
                evidence.extend(computational_result['quantitative_insights'][:3])

            # Add statistical evidence
            if 'statistical_evidence' in computational_result:
                stat_evidence = computational_result['statistical_evidence']
                evidence.append(f"Statistical evidence: {stat_evidence}")

            discovery = Discovery(
                id=f"discovery_{hashlib.md5(question.question.encode()).hexdigest()[:8]}",
                question=question,
                discovery=discovery_text,
                confidence=computational_result['confidence'],
                evidence=evidence,
                timestamp=datetime.now().timestamp(),
                validation_status="pending",
                computational_backing={
                    'analysis_type': computational_result['analysis_type'],
                    'quantitative_insights': computational_result.get('quantitative_insights', []),
                    'statistical_evidence': computational_result.get('statistical_evidence', {}),
                    'data_sources': computational_result.get('data_sources', []),
                    'novel_contribution': computational_result.get('novel_contribution', '')
                }
            )

            logger.info(f"✅ Discovery created with computational backing: confidence {discovery.confidence}")
            return discovery

        except Exception as e:
            logger.error(f"WORKING question exploration error: {e}", exc_info=True)
            return None

    def _generate_questions(self) -> List[CuriosityQuestion]:
        """Generate curiosity questions"""
        if not self.curiosity_engine:
            return []

        all_questions = self.curiosity_engine.generate_questions(max_questions=50)

        # Filter by scope
        filtered = [q for q in all_questions if self._within_scope(q)]

        # Return rotating subset
        if not hasattr(self, 'question_cycle_index'):
            self.question_cycle_index = 0

        batch_size = self.config.questions_per_cycle
        start_idx = self.question_cycle_index % len(filtered)
        end_idx = (start_idx + batch_size) % len(filtered)

        if end_idx > start_idx:
            batch = filtered[start_idx:end_idx]
        else:
            batch = filtered[start_idx:] + filtered[:end_idx]

        self.question_cycle_index = end_idx
        return batch

    def _within_scope(self, question: CuriosityQuestion) -> bool:
        """Check if question is within allowed scope"""
        for forbidden in self.config.forbidden_domains:
            if forbidden.lower() in question.question.lower():
                return False

        if self.config.allowed_domains:
            combined_text = f"{question.question} {question.context or ''}".lower()
            if not any(domain.lower() in combined_text for domain in self.config.allowed_domains):
                return False

        return True

    def _within_resource_limits(self) -> bool:
        """Check if within configured resource limits"""
        if self.weekly_cpu_hours >= self.config.max_hours_per_week:
            return False

        now = datetime.now()
        if (now - self.session_start_time).days >= 7:
            self.weekly_cpu_hours = 0.0
            self.session_start_time = now

        return True

    def _is_idle(self) -> bool:
        """Check if system has been idle long enough"""
        idle_time = (datetime.now() - self.last_activity_time).total_seconds()
        return idle_time >= self.config.idle_timeout_minutes * 60

    def _validate_discovery(self, discovery: Discovery) -> bool:
        """Validate discovery quality"""
        # Check confidence threshold
        if discovery.confidence < self.config.min_confidence_to_store:
            return False

        # Check evidence count
        if len(discovery.evidence) < self.config.min_evidence_count:
            return False

        # CRITICAL: Check if has computational backing
        if not discovery.computational_backing:
            logger.warning(f"Discovery {discovery.id} rejected: no computational backing")
            return False

        # Check if has quantitative insights
        if not discovery.computational_backing.get('quantitative_insights'):
            logger.warning(f"Discovery {discovery.id} rejected: no quantitative insights")
            return False

        # Check if has statistical evidence
        if not discovery.computational_backing.get('statistical_evidence'):
            logger.warning(f"Discovery {discovery.id} rejected: no statistical evidence")
            return False

        return True

    def _store_discovery(self, discovery: Discovery):
        """Store validated discovery"""
        discovery.validation_status = "validated"
        self.discoveries.append(discovery)

        # AUTOMATIC CONTEXT PRESERVATION - Update with discovery result
        # This completes the context with the autonomous discovery
        try:
            from biodisc_core.memory.persistent.context_preservation import update_context_field
            update_context_field(
                'last_assistant_response',
                f"Discovery: {discovery.discovery[:500]}..."  # First 500 chars
            )
            update_context_field(
                'current_task',
                f'Discovery validated: {discovery.id}'
            )
        except ImportError:
            # Context preservation module not available - silently continue
            pass
        except Exception:
            # Don't break discovery storage if context update fails
            pass

        # Log to file if configured
        if self.config.log_all_discoveries:
            try:
                with open(self.config.discovery_log_path, 'a') as f:
                    discovery_record = {
                        'id': discovery.id,
                        'question': discovery.question.question,
                        'discovery': discovery.discovery,
                        'confidence': discovery.confidence,
                        'evidence': discovery.evidence,
                        'timestamp': discovery.timestamp,
                        'computational_backing': discovery.computational_backing,
                        'validation_status': 'validated'
                    }
                    f.write(json.dumps(discovery_record) + '\n')
            except Exception as e:
                logger.error(f"Error writing discovery to log: {e}")

        logger.info(f"✅ Discovery stored: {discovery.id}")

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            'status': self.status.value,
            'running': self.running,
            'paused': self.paused,
            'total_discoveries': len(self.discoveries),
            'validated_discoveries': sum(1 for d in self.discoveries if d.validation_status == "validated"),
            'weekly_cpu_hours': self.weekly_cpu_hours,
            'last_activity': self.last_activity_time.isoformat(),
            'recent_discoveries': [
                {
                    'id': d.id,
                    'question': d.question.question,
                    'confidence': d.confidence,
                    'validated': d.validation_status == "validated",
                    'computational_backing': bool(d.computational_backing)
                }
                for d in self.discoveries[-5:]
            ]
        }


def get_working_autonomous_discovery_system(config=None) -> WorkingAutonomousDiscoveryOrchestrator:
    """Factory function to create WORKING autonomous discovery system"""
    return WorkingAutonomousDiscoveryOrchestrator(config)