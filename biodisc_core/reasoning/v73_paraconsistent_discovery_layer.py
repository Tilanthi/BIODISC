"""
V73 Paraconsistent Discovery Layer

Implements paraconsistent logic for autonomous discovery, allowing contradictions
to coexist and be preserved rather than eliminated. Based on insights from
"The Computational Model of Intelligence as Process-Substrate" (Viharo, 2026).

KEY FEATURES:
- Ternary logic (CERTAIN/LIKELY/MYSTERY) instead of binary true/false
- Contradiction tagging and containment
- Preserve contradictory findings as "active research areas"
- Paraconsistent metrics (CCR, RP, RL, CS)
- Act 3 synthesis for conflicting perspectives

Date: 2026-06-01
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from datetime import datetime
import json
import hashlib
import threading
from collections import defaultdict


class TruthState(Enum):
    """Ternary logic states for paraconsistent reasoning"""
    CERTAIN = "certain"       # Well-established, high confidence
    LIKELY = "likely"         # Probabilistic, moderate confidence
    MYSTERY = "mystery"      # Unknown, undecidable, or inherently ambiguous


class ContradictionTag(Enum):
    """Types of contradictions between discoveries"""
    DIRECT = "direct"           # Explicit logical contradiction
    CONTEXT_DEPENDENT = "context_dependent"  # True in different contexts
    EVIDENCE_CONFLICT = "evidence_conflict"  # Different evidence supports different views
    TEMPORAL = "temporal"       # Changes over time
    SCALE_DEPENDENT = "scale_dependent"  # True at different scales
    THEORETICAL = "theoretical"  # Different theoretical frameworks


@dataclass
class Contradiction:
    """A detected contradiction between discoveries"""
    contradiction_id: str
    discovery_1_id: str
    discovery_2_id: str
    contradiction_type: ContradictionTag
    description: str
    severity: float  # 0.0 to 1.0
    resolution_status: str  # "unresolved", "contained", "synthesized"
    synthesized_view: Optional[str] = None
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class ParaconsistentDiscovery:
    """A discovery with paraconsistent metadata"""
    # Original discovery data
    id: str
    question: str
    discovery: str
    confidence: float
    evidence: List[str]
    timestamp: float

    # Paraconsistent extensions
    truth_state: TruthState
    contradiction_ids: List[str] = field(default_factory=list)
    preserved_despite_contradiction: bool = False
    context_notes: List[str] = field(default_factory=list)

    # Synthesis tracking
    synthesized_from: List[str] = field(default_factory=list)  # IDs of discoveries synthesized into this
    is_synthesis: bool = False


@dataclass
class ParaconsistentMetrics:
    """Metrics for paraconsistent system performance"""
    # Contradiction Containment Rate (CCR)
    # How well contradictions are contained without system collapse
    contradiction_containment_rate: float = 0.0

    # Relevance Precision (RP)
    # How well system filters irrelevant contradictions
    relevance_precision: float = 0.0

    # Revision Latency (RL)
    # How quickly system revises beliefs given new evidence
    revision_latency: float = 0.0  # in seconds

    # Consensus Stability (CS)
    # How stable consensus is over time (0 = unstable, 1 = very stable)
    consensus_stability: float = 0.0

    # Additional metrics
    total_contradictions_detected: int = 0
    contradictions_synthesized: int = 0
    contradictions_preserved: int = 0
    mysteries_preserved: int = 0


class ContradictionDetector:
    """
    Detects contradictions between discoveries using paraconsistent logic.

    Unlike classical logic which collapses under contradiction, this system:
    - Identifies contradiction type
    - Tags contradictions for containment
    - Preserves both perspectives
    """

    def __init__(self):
        self.contradiction_patterns = {
            ContradictionTag.DIRECT: [
                "not", "never", "cannot", "impossible", "false"
            ],
            ContradictionTag.CONTEXT_DEPENDENT: [
                "in some contexts", "under certain conditions", "depends on"
            ],
            ContradictionTag.EVIDENCE_CONFLICT: [
                "evidence suggests", "data indicates", "studies show"
            ],
            ContradictionTag.TEMPORAL: [
                "over time", "evolves", "changes", "transitional"
            ],
            ContradictionTag.SCALE_DEPENDENT: [
                "at molecular scale", "at cellular level", "at population level"
            ],
            ContradictionTag.THEORETICAL: [
                "according to", "framework", "paradigm", "model"
            ]
        }

    def detect_contradictions(
        self,
        discovery1: ParaconsistentDiscovery,
        discovery2: ParaconsistentDiscovery
    ) -> List[Contradiction]:
        """
        Detect contradictions between two discoveries.

        Returns list of detected contradictions (may be multiple types).
        """
        contradictions = []

        # Check for direct logical contradiction
        if self._check_direct_contradiction(discovery1, discovery2):
            contradictions.append(Contradiction(
                contradiction_id=self._generate_contradiction_id(discovery1.id, discovery2.id, "direct"),
                discovery_1_id=discovery1.id,
                discovery_2_id=discovery2.id,
                contradiction_type=ContradictionTag.DIRECT,
                description=f"Direct contradiction between '{discovery1.question[:50]}...' and '{discovery2.question[:50]}...'",
                severity=0.8,
                resolution_status="unresolved"
            ))

        # Check for context-dependent contradictions
        if self._check_context_dependent(discovery1, discovery2):
            contradictions.append(Contradiction(
                contradiction_id=self._generate_contradiction_id(discovery1.id, discovery2.id, "context"),
                discovery_1_id=discovery1.id,
                discovery_2_id=discovery2.id,
                contradiction_type=ContradictionTag.CONTEXT_DEPENDENT,
                description=f"Context-dependent contradiction: may both be true in different contexts",
                severity=0.5,
                resolution_status="unresolved"
            ))

        # Check for evidence conflicts
        if self._check_evidence_conflict(discovery1, discovery2):
            contradictions.append(Contradiction(
                contradiction_id=self._generate_contradiction_id(discovery1.id, discovery2.id, "evidence"),
                discovery_1_id=discovery1.id,
                discovery_2_id=discovery2.id,
                contradiction_type=ContradictionTag.EVIDENCE_CONFLICT,
                description=f"Different evidence bases support different conclusions",
                severity=0.6,
                resolution_status="unresolved"
            ))

        # Check for scale-dependent contradictions
        if self._check_scale_dependent(discovery1, discovery2):
            contradictions.append(Contradiction(
                contradiction_id=self._generate_contradiction_id(discovery1.id, discovery2.id, "scale"),
                discovery_1_id=discovery1.id,
                discovery_2_id=discovery2.id,
                contradiction_type=ContradictionTag.SCALE_DEPENDENT,
                description=f"Scale-dependent contradiction: may both be true at different scales",
                severity=0.4,
                resolution_status="unresolved"
            ))

        return contradictions

    def _check_direct_contradiction(
        self,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> bool:
        """Check for direct logical contradiction"""
        # Look for negation patterns
        d1_lower = d1.discovery.lower()
        d2_lower = d2.discovery.lower()

        negation_words = ["not ", "never", "cannot", "impossible", "false", "no "]

        # Check if one explicitly negates concepts from the other
        for negation in negation_words:
            if negation in d1_lower or negation in d2_lower:
                # Check if they're discussing similar concepts
                if self._conceptual_overlap(d1, d2) > 0.3:
                    return True

        return False

    def _check_context_dependent(
        self,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> bool:
        """Check for context-dependent contradictions"""
        combined = d1.discovery.lower() + " " + d2.discovery.lower()
        context_words = ["context", "condition", "depends", "however", "although", "whereas"]
        return any(word in combined for word in context_words)

    def _check_evidence_conflict(
        self,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> bool:
        """Check for evidence-based conflicts"""
        # Both cite evidence but reach different conclusions
        d1_evidence = any("evidence" in e.lower() or "study" in e.lower()
                         for e in d1.evidence)
        d2_evidence = any("evidence" in e.lower() or "study" in e.lower()
                         for e in d2.evidence)

        return d1_evidence and d2_evidence and self._conceptual_overlap(d1, d2) > 0.2

    def _check_scale_dependent(
        self,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> bool:
        """Check for scale-dependent contradictions"""
        scale_indicators = [
            "molecular", "cellular", "tissue", "organism", "population",
            "micro", "macro", "level", "scale"
        ]

        d1_has_scale = any(word in d1.discovery.lower() for word in scale_indicators)
        d2_has_scale = any(word in d2.discovery.lower() for word in scale_indicators)

        return d1_has_scale and d2_has_scale

    def _conceptual_overlap(self, d1: ParaconsistentDiscovery, d2: ParaconsistentDiscovery) -> float:
        """Calculate conceptual overlap between discoveries (0.0 to 1.0)"""
        # Simple word overlap as proxy for conceptual overlap
        words1 = set(d1.discovery.lower().split())
        words2 = set(d2.discovery.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _generate_contradiction_id(self, id1: str, id2: str, tag: str) -> str:
        """Generate unique contradiction ID"""
        combined = f"{id1}_{id2}_{tag}"
        return f"contradiction_{hashlib.md5(combined.encode()).hexdigest()[:8]}"


class Act3Synthesizer:
    """
    Implements "Act 3" synthesis from Conversational Game Theory.

    When contradictions exist, Act 3 generates documents that:
    - Preserve multiple perspectives
    - Highlight shared coherence
    - Identify genuine disagreements
    - Propose synthesis without erasing difference

    This is paraconsistent synthesis: the whole contains contradictions
    without collapsing.
    """

    def __init__(self):
        self.synthesis_templates = {
            "context_dependent": """
## Context-Dependent Perspectives

Both {discovery1} and {discovery2} appear valid, but may apply under different conditions:

**Perspective 1:** {view1}

**Perspective 2:** {view2}

**Synthesis:** These findings suggest {synthesis_hypothesis}. Further research is needed
to identify the boundary conditions that determine which perspective applies.

**Shared Coherence:** Both perspectives agree on {common_ground}.

**Open Question:** {open_question}
""",

            "scale_dependent": """
## Scale-Dependent Phenomenon

The apparent contradiction between {discovery1} and {discovery2} may reflect different
organizational scales:

**At {scale1} scale:** {view1}

**At {scale2} scale:** {view2}

**Synthesis:** This suggests {synthesis_hypothesis}. The phenomenon may exhibit
scale-dependent behavior where mechanisms differ across organizational levels.

**Cross-Scale Connection:** {common_ground}

**Open Question:** {open_question}
""",

            "evidence_conflict": """
## Conflicting Evidence

Current evidence supports multiple perspectives on {topic}:

**Evidence Set 1:** {view1}
- Supporting evidence: {evidence1}

**Evidence Set 2:** {view2}
- Supporting evidence: {evidence2}

**Synthesis:** The conflict may arise from {synthesis_hypothesis}. Additional research
is needed to reconcile these findings.

**Methodological Considerations:** {common_ground}

**Open Question:** {open_question}
""",

            "default": """
## Multiple Perspectives

The relationship between {discovery1} and {discovery2} presents an interesting case:

**View 1:** {view1}

**View 2:** {view2}

**Synthesis:** {synthesis_hypothesis}

**Common Ground:** {common_ground}

**Open Question:** {open_question}
"""
        }

    def create_synthesis(
        self,
        contradiction: Contradiction,
        discovery1: ParaconsistentDiscovery,
        discovery2: ParaconsistentDiscovery
    ) -> str:
        """
        Create Act 3 synthesis document for a contradiction.

        Returns synthesis text that preserves both perspectives.
        """
        # Extract key elements
        view1 = discovery1.discovery[:200] + "..." if len(discovery1.discovery) > 200 else discovery1.discovery
        view2 = discovery2.discovery[:200] + "..." if len(discovery2.discovery) > 200 else discovery2.discovery

        # Find common ground
        common_ground = self._find_common_ground(discovery1, discovery2)

        # Generate synthesis hypothesis
        synthesis_hypothesis = self._generate_synthesis_hypothesis(
            contradiction, discovery1, discovery2
        )

        # Generate open question
        open_question = self._generate_open_question(contradiction, discovery1, discovery2)

        # Select template based on contradiction type
        template_key = contradiction.contradiction_type.value
        template = self.synthesis_templates.get(
            template_key,
            self.synthesis_templates["default"]
        )

        # Fill template
        synthesis = template.format(
            discovery1=discovery1.question[:50],
            discovery2=discovery2.question[:50],
            view1=view1,
            view2=view2,
            synthesis_hypothesis=synthesis_hypothesis,
            common_ground=common_ground,
            open_question=open_question,
            scale1=self._detect_scale(discovery1),
            scale2=self._detect_scale(discovery2),
            topic=discovery1.question[:50],
            evidence1=", ".join(discovery1.evidence[:2]),
            evidence2=", ".join(discovery2.evidence[:2])
        )

        return synthesis.strip()

    def _find_common_ground(
        self,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> str:
        """Identify common elements between discoveries"""
        # Look for shared concepts
        words1 = set(d1.discovery.lower().split())
        words2 = set(d2.discovery.lower().split())

        common = words1.intersection(words2)

        # Filter meaningful words
        meaningful = [w for w in common if len(w) > 3]

        if meaningful:
            return f"Both perspectives address: {', '.join(meaningful[:5])}"
        else:
            return "Both perspectives investigate related biological phenomena"

    def _generate_synthesis_hypothesis(
        self,
        contradiction: Contradiction,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> str:
        """Generate a synthesis hypothesis"""
        if contradiction.contradiction_type == ContradictionTag.CONTEXT_DEPENDENT:
            return "both findings may be valid under different environmental or experimental conditions"
        elif contradiction.contradiction_type == ContradictionTag.SCALE_DEPENDENT:
            return "different mechanisms may operate at different organizational scales"
        elif contradiction.contradiction_type == ContradictionTag.EVIDENCE_CONFLICT:
            return "methodological differences or population variability may explain the discrepancy"
        else:
            return "further research is needed to reconcile these findings"

    def _generate_open_question(
        self,
        contradiction: Contradiction,
        d1: ParaconsistentDiscovery,
        d2: ParaconsistentDiscovery
    ) -> str:
        """Generate an open question for future research"""
        return f"What conditions determine when {d1.question[:40].lower()} versus {d2.question[:40].lower()} applies?"

    def _detect_scale(self, discovery: ParaconsistentDiscovery) -> str:
        """Detect the organizational scale of a discovery"""
        text = discovery.discovery.lower()

        if "molecular" in text or "atomic" in text:
            return "molecular"
        elif "cell" in text or "cellular" in text:
            return "cellular"
        elif "tissue" in text or "organ" in text:
            return "tissue/organ"
        elif "population" in text or "organism" in text:
            return "organismal"
        else:
            return "system-level"


class ParaconsistentDiscoveryLayer:
    """
    Main layer for paraconsistent discovery management.

    INTEGRATES:
    - Contradiction detection and tagging
    - Ternary logic state assignment
    - Contradiction containment
    - Act 3 synthesis generation
    - Paraconsistent metrics tracking
    """

    def __init__(self):
        self.detector = ContradictionDetector()
        self.synthesizer = Act3Synthesizer()

        # Storage
        self.discoveries: Dict[str, ParaconsistentDiscovery] = {}
        self.contradictions: Dict[str, Contradiction] = {}
        self.syntheses: Dict[str, str] = {}  # synthesis_id -> synthesis text

        # Metrics
        self.metrics = ParaconsistentMetrics()

        # Thread safety
        self.lock = threading.Lock()

        # History for metrics
        self.contradiction_history: List[Tuple[str, float]] = []  # (timestamp, count)
        self.revision_history: List[Tuple[str, float]] = []  # (timestamp, latency)
        self.consensus_history: List[Tuple[str, float]] = []  # (timestamp, stability)

    def add_discovery(
        self,
        question: str,
        discovery: str,
        confidence: float,
        evidence: List[str],
        timestamp: float = None
    ) -> ParaconsistentDiscovery:
        """
        Add a new discovery and check for contradictions.

        Returns the ParaconsistentDiscovery with assigned truth state.
        """
        with self.lock:
            # Create discovery ID
            discovery_id = f"discovery_{hashlib.md5(question.encode()).hexdigest()[:8]}"

            # Assign truth state based on confidence
            truth_state = self._assign_truth_state(confidence)

            # Create paraconsistent discovery
            pd = ParaconsistentDiscovery(
                id=discovery_id,
                question=question,
                discovery=discovery,
                confidence=confidence,
                evidence=evidence,
                timestamp=timestamp or datetime.now().timestamp(),
                truth_state=truth_state
            )

            # Store discovery
            self.discoveries[discovery_id] = pd

            # Check for contradictions with existing discoveries
            self._check_and_store_contradictions(pd)

            # Update metrics
            self._update_metrics()

            return pd

    def _assign_truth_state(self, confidence: float) -> TruthState:
        """Assign ternary truth state based on confidence"""
        if confidence >= 0.85:
            return TruthState.CERTAIN
        elif confidence >= 0.60:
            return TruthState.LIKELY
        else:
            return TruthState.MYSTERY

    def _check_and_store_contradictions(self, new_discovery: ParaconsistentDiscovery):
        """Check new discovery against all existing discoveries for contradictions"""
        for existing_id, existing_discovery in self.discoveries.items():
            if existing_id == new_discovery.id:
                continue

            # Detect contradictions
            contradictions = self.detector.detect_contradictions(
                new_discovery, existing_discovery
            )

            # Store contradictions
            for contradiction in contradictions:
                self.contradictions[contradiction.contradiction_id] = contradiction

                # Link contradictions to discoveries
                if contradiction.contradiction_id not in new_discovery.contradiction_ids:
                    new_discovery.contradiction_ids.append(contradiction.contradiction_id)
                if contradiction.contradiction_id not in existing_discovery.contradiction_ids:
                    existing_discovery.contradiction_ids.append(contradiction.contradiction_id)

    def synthesize_contradiction(
        self,
        contradiction_id: str
    ) -> Optional[str]:
        """
        Create Act 3 synthesis for a contradiction.

        Returns synthesis text if successful.
        """
        with self.lock:
            if contradiction_id not in self.contradictions:
                return None

            contradiction = self.contradictions[contradiction_id]

            # Get the two discoveries
            d1 = self.discoveries.get(contradiction.discovery_1_id)
            d2 = self.discoveries.get(contradiction.discovery_2_id)

            if not d1 or not d2:
                return None

            # Create synthesis
            synthesis = self.synthesizer.create_synthesis(
                contradiction, d1, d2
            )

            # Store synthesis
            self.syntheses[contradiction_id] = synthesis

            # Update contradiction status
            contradiction.resolution_status = "synthesized"
            contradiction.synthesized_view = synthesis

            # Update metrics
            self.metrics.contradictions_synthesized += 1

            return synthesis

    def get_active_contradictions(self) -> List[Contradiction]:
        """Get all unresolved contradictions"""
        with self.lock:
            return [
                c for c in self.contradictions.values()
                if c.resolution_status == "unresolved"
            ]

    def get_discoveries_by_truth_state(
        self,
        truth_state: TruthState
    ) -> List[ParaconsistentDiscovery]:
        """Get all discoveries with a specific truth state"""
        with self.lock:
            return [
                d for d in self.discoveries.values()
                if d.truth_state == truth_state
            ]

    def get_paraconsistent_report(self) -> Dict[str, Any]:
        """Generate comprehensive paraconsistent system report"""
        with self.lock:
            # Count by truth state
            state_counts = defaultdict(int)
            for d in self.discoveries.values():
                state_counts[d.truth_state.value] += 1

            # Count contradictions by type
            contradiction_counts = defaultdict(int)
            for c in self.contradictions.values():
                contradiction_counts[c.contradiction_type.value] += 1

            return {
                "total_discoveries": len(self.discoveries),
                "discoveries_by_truth_state": dict(state_counts),
                "total_contradictions": len(self.contradictions),
                "contradictions_by_type": dict(contradiction_counts),
                "unresolved_contradictions": len(self.get_active_contradictions()),
                "syntheses_created": len(self.syntheses),
                "metrics": {
                    "contradiction_containment_rate": self.metrics.contradiction_containment_rate,
                    "relevance_precision": self.metrics.relevance_precision,
                    "revision_latency": self.metrics.revision_latency,
                    "consensus_stability": self.metrics.consensus_stability,
                    "total_contradictions_detected": self.metrics.total_contradictions_detected,
                    "contradictions_synthesized": self.metrics.contradictions_synthesized,
                    "contradictions_preserved": self.metrics.contradictions_preserved,
                    "mysteries_preserved": self.metrics.mysteries_preserved
                },
                "active_research_areas": self._get_active_research_areas()
            }

    def _get_active_research_areas(self) -> List[str]:
        """Get topics with unresolved contradictions (active research areas)"""
        areas = []
        for contradiction in self.get_active_contradictions():
            d1 = self.discoveries.get(contradiction.discovery_1_id)
            if d1:
                areas.append(d1.question[:60])
        return areas[:10]  # Top 10

    def _update_metrics(self):
        """Update paraconsistent performance metrics"""
        # Update contradiction count
        self.metrics.total_contradictions_detected = len(self.contradictions)

        # Calculate contradiction containment rate
        # (contradictions contained / total contradictions)
        if self.metrics.total_contradictions_detected > 0:
            contained = sum(
                1 for c in self.contradictions.values()
                if c.resolution_status in ["contained", "synthesized"]
            )
            self.metrics.contradiction_containment_rate = (
                contained / self.metrics.total_contradictions_detected
            )

        # Track mysteries (MYSTERY truth state)
        self.metrics.mysteries_preserved = len(
            self.get_discoveries_by_truth_state(TruthState.MYSTERY)
        )

        # Track preserved contradictions
        self.metrics.contradictions_preserved = len(self.get_active_contradictions())

        # Add to history for temporal metrics
        now = datetime.now().timestamp()
        self.contradiction_history.append((now, len(self.contradictions)))


# =============================================================================
# Factory Functions
# =============================================================================

def create_paraconsistent_discovery_layer() -> ParaconsistentDiscoveryLayer:
    """Create a new paraconsistent discovery layer"""
    return ParaconsistentDiscoveryLayer()


# Singleton instance
_instance = None
_lock = threading.Lock()

def get_paraconsistent_discovery_layer() -> ParaconsistentDiscoveryLayer:
    """Get or create singleton instance"""
    global _instance
    with _lock:
        if _instance is None:
            _instance = create_paraconsistent_discovery_layer()
        return _instance
