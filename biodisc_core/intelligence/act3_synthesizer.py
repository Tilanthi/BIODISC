"""
Act 3 Synthesizer for Multi-Mind Orchestrator

Implements "Act 3" synthesis from Conversational Game Theory (CGT).
When multiple minds disagree, Act 3 generates documents that:

- Preserve multiple perspectives
- Highlight shared coherence
- Identify genuine disagreements
- Propose synthesis without erasing difference

This is paraconsistent synthesis: the whole contains contradictions
without collapsing. Inspired by "The Computational Model of Intelligence
as Process-Substrate" (Viharo, 2026).

Date: 2026-06-01
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import json
import hashlib

try:
    from .specialized_minds import MindResult, Domain, ReasoningStyle
    SPECIALIZED_MINDS_AVAILABLE = True
except ImportError:
    SPECIALIZED_MINDS_AVAILABLE = False


class SynthesisStrategy(Enum):
    """Strategies for synthesizing multiple perspectives"""
    PRESERVE_ALL = "preserve_all"  # Keep all perspectives distinct
    HIGHLIGHT_COHERENCE = "highlight_coherence"  # Emphasize common ground
    IDENTIFY_DISAGREEMENTS = "identify_disagreements"  # Explicit disagreements
    CONTEXTUALIZE = "contextualize"  # Explain when each applies
    INTEGRATE = "integrate"  # Create higher-order synthesis


@dataclass
class Perspective:
    """A single perspective from a mind"""
    mind_id: str
    domain: str
    reasoning_style: str
    result: Any
    confidence: float
    reasoning_process: List[str]
    key_insights: List[str]
    assumptions: List[str]


@dataclass
class Act3Synthesis:
    """Result of Act 3 synthesis"""
    synthesis_id: str
    query: str
    perspectives: List[Perspective]
    synthesis_strategy: SynthesisStrategy

    # Synthesis components
    shared_coherence: List[str]  # What all perspectives agree on
    genuine_disagreements: List[Dict[str, Any]]  # Where they genuinely differ
    contextual_notes: List[str]  # Context for each perspective
    integrated_insights: List[str]  # Higher-order insights

    # Preserved perspectives
    preserved_views: List[str]  # Each perspective preserved

    # Metrics
    coherence_score: float  # How much coherence exists (0-1)
    disagreement_count: int  # Number of genuine disagreements
    synthesis_quality: float  # Quality of synthesis (0-1)

    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class PerspectiveExtractor:
    """
    Extract structured perspectives from mind results.

    Converts raw mind outputs into structured Perspective objects
    for synthesis.
    """

    def extract_perspective(
        self,
        mind_id: str,
        result: Any
    ) -> Optional[Perspective]:
        """
        Extract a structured perspective from a mind result.

        Args:
            mind_id: ID of the mind
            result: Raw result from mind

        Returns:
            Perspective object or None if extraction fails
        """
        if result is None:
            return None

        # Handle different result types
        if isinstance(result, dict):
            return self._extract_from_dict(mind_id, result)
        elif SPECIALIZED_MINDS_AVAILABLE and isinstance(result, MindResult):
            return self._extract_from_mind_result(mind_id, result)
        else:
            return self._extract_from_generic(mind_id, result)

    def _extract_from_dict(self, mind_id: str, result: Dict) -> Perspective:
        """Extract perspective from dict result"""
        return Perspective(
            mind_id=mind_id,
            domain=result.get('domain', 'unknown'),
            reasoning_style=result.get('reasoning_style', 'unknown'),
            result=result.get('result', result),
            confidence=result.get('confidence', 0.5),
            reasoning_process=result.get('reasoning_process', []),
            key_insights=result.get('key_insights', []),
            assumptions=result.get('assumptions', [])
        )

    def _extract_from_mind_result(self, mind_id: str, result: 'MindResult') -> Perspective:
        """Extract perspective from MindResult"""
        return Perspective(
            mind_id=mind_id,
            domain=result.domain.value if hasattr(result, 'domain') else 'unknown',
            reasoning_style=result.reasoning_style.value if hasattr(result, 'reasoning_style') else 'unknown',
            result=result.result,
            confidence=result.confidence,
            reasoning_process=result.reasoning_process if hasattr(result, 'reasoning_process') else [],
            key_insights=[],  # Would extract from result
            assumptions=[]  # Would extract from result
        )

    def _extract_from_generic(self, mind_id: str, result: Any) -> Perspective:
        """Extract perspective from generic result"""
        # Convert to string and extract basic info
        result_str = str(result)

        return Perspective(
            mind_id=mind_id,
            domain='unknown',
            reasoning_style='unknown',
            result=result,
            confidence=0.5,  # Default confidence
            reasoning_process=[result_str[:200]],  # First 200 chars as process
            key_insights=[],
            assumptions=[]
        )


class CoherenceAnalyzer:
    """
    Analyzes coherence and disagreements across perspectives.

    Identifies what perspectives agree on (shared coherence) and
    where they genuinely disagree (genuine disagreements).
    """

    def analyze_coherence(
        self,
        perspectives: List[Perspective]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Analyze perspectives for coherence and disagreements.

        Returns:
            (shared_coherence, genuine_disagreements)
        """
        if not perspectives:
            return [], []

        # Find shared coherence
        shared_coherence = self._find_shared_coherence(perspectives)

        # Find genuine disagreements
        genuine_disagreements = self._find_disagreements(perspectives)

        return shared_coherence, genuine_disagreements

    def _find_shared_coherence(self, perspectives: List[Perspective]) -> List[str]:
        """Find what all perspectives agree on"""
        coherence = []

        # Check if all have high confidence
        if all(p.confidence > 0.7 for p in perspectives):
            coherence.append("All perspectives express high confidence in their reasoning")

        # Find common themes in reasoning processes
        all_themes = []
        for p in perspectives:
            all_themes.extend(p.reasoning_process)

        # Simple word overlap as proxy for theme overlap
        from collections import Counter
        word_counts = Counter()
        for theme in all_themes:
            words = theme.lower().split()
            for word in words:
                if len(word) > 3:  # Ignore short words
                    word_counts[word] += 1

        # Themes mentioned by multiple perspectives
        common_themes = [word for word, count in word_counts.items() if count >= len(perspectives)]
        if common_themes:
            coherence.append(f"Common themes across perspectives: {', '.join(common_themes[:5])}")

        # Check domain coherence
        domains = [p.domain for p in perspectives]
        if len(set(domains)) == 1:
            coherence.append(f"All perspectives operate within the {domains[0]} domain")
        else:
            coherence.append(f"Perspectives span multiple domains: {', '.join(set(domains))}")

        return coherence

    def _find_disagreements(
        self,
        perspectives: List[Perspective]
    ) -> List[Dict[str, Any]]:
        """Find genuine disagreements between perspectives"""
        disagreements = []

        # Compare each pair of perspectives
        for i, p1 in enumerate(perspectives):
            for p2 in perspectives[i+1:]:
                disagreement = self._compare_perspectives(p1, p2)
                if disagreement:
                    disagreements.append(disagreement)

        return disagreements

    def _compare_perspectives(
        self,
        p1: Perspective,
        p2: Perspective
    ) -> Optional[Dict[str, Any]]:
        """Compare two perspectives for disagreements"""
        disagreements = []

        # Check confidence disagreement
        if abs(p1.confidence - p2.confidence) > 0.3:
            disagreements.append({
                'type': 'confidence',
                'description': f"Different confidence levels: {p1.mind_id} ({p1.confidence:.2f}) vs {p2.mind_id} ({p2.confidence:.2f})"
            })

        # Check domain disagreement
        if p1.domain != p2.domain:
            disagreements.append({
                'type': 'domain',
                'description': f"Different domains: {p1.domain} vs {p2.domain}",
                'context': f"Each perspective may prioritize different aspects of the query"
            })

        # Check reasoning style disagreement
        if p1.reasoning_style != p2.reasoning_style:
            disagreements.append({
                'type': 'methodology',
                'description': f"Different reasoning styles: {p1.reasoning_style} vs {p2.reasoning_style}",
                'context': f"Different approaches may lead to different conclusions"
            })

        # Check result disagreement (basic)
        if str(p1.result)[:100] != str(p2.result)[:100]:
            disagreements.append({
                'type': 'conclusion',
                'description': f"Different conclusions reached",
                'context': f"{p1.mind_id} and {p2.mind_id} arrived at different answers"
            })

        if disagreements:
            return {
                'perspective_1': p1.mind_id,
                'perspective_2': p2.mind_id,
                'disagreements': disagreements
            }

        return None


class Act3SynthesisGenerator:
    """
    Generates Act 3 synthesis documents that preserve multiple perspectives.

    ACT 3 STRUCTURE:
    1. Executive Summary
    2. Preserved Perspectives (each mind's view)
    3. Shared Coherence (what they agree on)
    4. Genuine Disagreements (where they differ)
    5. Contextual Notes (when each applies)
    6. Integrated Insights (higher-order synthesis)
    """

    def __init__(self):
        self.extractor = PerspectiveExtractor()
        self.analyzer = CoherenceAnalyzer()

    def create_synthesis(
        self,
        query: str,
        mind_results: Dict[str, Any]
    ) -> Act3Synthesis:
        """
        Create Act 3 synthesis from multiple mind results.

        Args:
            query: The original query
            mind_results: Dictionary mapping mind_id to result

        Returns:
            Act3Synthesis object
        """
        # Extract perspectives
        perspectives = []
        for mind_id, result in mind_results.items():
            perspective = self.extractor.extract_perspective(mind_id, result)
            if perspective:
                perspectives.append(perspective)

        if not perspectives:
            return self._empty_synthesis(query)

        # Analyze coherence
        shared_coherence, genuine_disagreements = self.analyzer.analyze_coherence(perspectives)

        # Generate synthesis
        synthesis = Act3Synthesis(
            synthesis_id=f"synthesis_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            query=query,
            perspectives=perspectives,
            synthesis_strategy=self._select_strategy(perspectives, genuine_disagreements),
            shared_coherence=shared_coherence,
            genuine_disagreements=genuine_disagreements,
            contextual_notes=self._generate_contextual_notes(perspectives),
            integrated_insights=self._generate_integrated_insights(perspectives, shared_coherence, genuine_disagreements),
            preserved_views=self._preserve_views(perspectives),
            coherence_score=self._calculate_coherence_score(shared_coherence, len(perspectives)),
            disagreement_count=len(genuine_disagreements),
            synthesis_quality=0.0  # Will calculate
        )

        # Calculate synthesis quality
        synthesis.synthesis_quality = self._calculate_synthesis_quality(synthesis)

        return synthesis

    def _select_strategy(
        self,
        perspectives: List[Perspective],
        disagreements: List[Dict[str, Any]]
    ) -> SynthesisStrategy:
        """Select appropriate synthesis strategy"""
        if not disagreements:
            return SynthesisStrategy.HIGHLIGHT_COHERENCE
        elif len(disagreements) > len(perspectives):
            return SynthesisStrategy.PRESERVE_ALL
        elif len(set(p.domain for p in perspectives)) > 2:
            return SynthesisStrategy.CONTEXTUALIZE
        else:
            return SynthesisStrategy.INTEGRATE

    def _generate_contextual_notes(self, perspectives: List[Perspective]) -> List[str]:
        """Generate contextual notes for each perspective"""
        notes = []

        for p in perspectives:
            note = f"{p.mind_id} ({p.domain}): Uses {p.reasoning_style} reasoning"
            if p.confidence < 0.5:
                note += " - expresses low confidence"
            elif p.confidence > 0.8:
                note += " - expresses high confidence"
            notes.append(note)

        return notes

    def _generate_integrated_insights(
        self,
        perspectives: List[Perspective],
        coherence: List[str],
        disagreements: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate higher-order integrated insights"""
        insights = []

        # Insight from coherence
        if coherence:
            insights.append(f"Multiple perspectives converge on: {coherence[0]}")

        # Insight from disagreements
        if disagreements:
            if len(disagreements) == 1:
                insights.append("One key disagreement exists that may benefit from further investigation")
            else:
                insights.append(f"{len(disagreements)} disagreements exist, suggesting complexity or context-dependence")

        # Domain diversity insight
        domains = set(p.domain for p in perspectives)
        if len(domains) > 1:
            insights.append(f"The question spans {len(domains)} domains, suggesting interdisciplinary relevance")

        # Confidence pattern insight
        confidences = [p.confidence for p in perspectives]
        if max(confidences) - min(confidences) > 0.5:
            insights.append("Perspectives vary significantly in confidence, indicating uncertainty or context-dependence")

        return insights

    def _preserve_views(self, perspectives: List[Perspective]) -> List[str]:
        """Generate preserved view for each perspective"""
        views = []

        for p in perspectives:
            view = f"## {p.mind_id} Perspective\n\n"
            view += f"**Domain:** {p.domain}\n"
            view += f"**Reasoning Style:** {p.reasoning_style}\n"
            view += f"**Confidence:** {p.confidence:.2f}\n\n"
            view += f"**Key Points:**\n"

            # Extract key points from reasoning process
            if p.reasoning_process:
                for point in p.reasoning_process[:3]:
                    view += f"- {point}\n"
            else:
                view += f"- {str(p.result)[:200]}\n"

            views.append(view)

        return views

    def _calculate_coherence_score(self, coherence: List[str], num_perspectives: int) -> float:
        """Calculate coherence score (0-1)"""
        if not coherence:
            return 0.0

        # More coherence items = higher score
        base_score = min(len(coherence) / (num_perspectives + 1), 1.0)

        return base_score

    def _calculate_synthesis_quality(self, synthesis: Act3Synthesis) -> float:
        """Calculate overall synthesis quality (0-1)"""
        # Quality factors:
        # - Coherence score (higher is better)
        # - Appropriate strategy selection
        # - Balance of preserved vs integrated content

        quality = 0.0

        # Coherence contributes
        quality += synthesis.coherence_score * 0.4

        # Strategic balance
        if synthesis.synthesis_strategy == SynthesisStrategy.INTEGRATE:
            quality += 0.3
        elif synthesis.synthesis_strategy == SynthesisStrategy.CONTEXTUALIZE:
            quality += 0.2

        # Content balance
        has_coherence = len(synthesis.shared_coherence) > 0
        has_disagreements = len(synthesis.genuine_disagreements) > 0
        has_insights = len(synthesis.integrated_insights) > 0

        if has_coherence and has_disagreements and has_insights:
            quality += 0.3
        elif has_coherence and has_insights:
            quality += 0.2

        return min(quality, 1.0)

    def _empty_synthesis(self, query: str) -> Act3Synthesis:
        """Create empty synthesis when no perspectives available"""
        return Act3Synthesis(
            synthesis_id=f"synthesis_empty_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            query=query,
            perspectives=[],
            synthesis_strategy=SynthesisStrategy.PRESERVE_ALL,
            shared_coherence=[],
            genuine_disagreements=[],
            contextual_notes=["No perspectives available"],
            integrated_insights=["Insufficient data for synthesis"],
            preserved_views=[],
            coherence_score=0.0,
            disagreement_count=0,
            synthesis_quality=0.0
        )

    def format_synthesis_as_markdown(self, synthesis: Act3Synthesis) -> str:
        """
        Format synthesis as markdown document.

        This is the "Act 3" document that preserves multiple perspectives.
        """
        md = f"# Act 3 Synthesis: {synthesis.query}\n\n"
        md += f"**Generated:** {datetime.fromtimestamp(synthesis.timestamp).isoformat()}\n"
        md += f"**Strategy:** {synthesis.synthesis_strategy.value}\n"
        md += f"**Coherence Score:** {synthesis.coherence_score:.2f}\n"
        md += f"**Synthesis Quality:** {synthesis.synthesis_quality:.2f}\n\n"

        # Executive Summary
        md += "## Executive Summary\n\n"
        if synthesis.integrated_insights:
            for insight in synthesis.integrated_insights:
                md += f"- {insight}\n"
        else:
            md += "No integrated insights available.\n"
        md += "\n"

        # Shared Coherence
        md += "## Shared Coherence\n\n"
        if synthesis.shared_coherence:
            for coherence in synthesis.shared_coherence:
                md += f"- {coherence}\n"
        else:
            md += "No significant coherence detected.\n"
        md += "\n"

        # Genuine Disagreements
        md += "## Genuine Disagreements\n\n"
        if synthesis.genuine_disagreements:
            for disagreement in synthesis.genuine_disagreements:
                md += f"### Between {disagreement['perspective_1']} and {disagreement['perspective_2']}\n\n"
                for item in disagreement['disagreements']:
                    md += f"- **{item['type'].title()}:** {item['description']}\n"
                    if 'context' in item:
                        md += f"  - *Context:* {item['context']}\n"
                md += "\n"
        else:
            md += "No genuine disagreements detected.\n"
        md += "\n"

        # Contextual Notes
        md += "## Contextual Notes\n\n"
        for note in synthesis.contextual_notes:
            md += f"- {note}\n"
        md += "\n"

        # Preserved Perspectives
        md += "## Preserved Perspectives\n\n"
        for i, view in enumerate(synthesis.preserved_views, 1):
            md += f"### Perspective {i}\n\n{view}\n\n"

        return md


# =============================================================================
# Factory Functions
# =============================================================================

def create_act3_synthesizer() -> Act3SynthesisGenerator:
    """Create a new Act 3 synthesizer"""
    return Act3SynthesisGenerator()


# Singleton instance
_instance = None

def get_act3_synthesizer() -> Act3SynthesisGenerator:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_act3_synthesizer()
    return _instance
