"""
V70 Teleology Filter - Detect and Reframe Purpose-Based Language

CRITICAL ISSUE from bacterial cell cycle review:
- Used teleological framing ("in order to", "designed to", "for the purpose of")
- Expert explicitly requested reframing to avoid implying purpose or design
- Biological mechanisms should be described in mechanistic, not teleological terms

CAPABILITIES:
- Automatically detect teleological framing
- Convert to mechanistic explanations
- Flag teleological language with confidence scores
- Suggest reframing for each detected instance

PRINCIPLE:
BAD: "Cells divide in order to reproduce"
GOOD: "Cells divide, which results in reproduction"

BAD: "Evolves to achieve greater fitness"
GOOD: "Variants with greater fitness increase in frequency"

Date: 2026-04-26
Version: 1.0.0
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class TeleologyType(Enum):
    """Types of teleological framing"""
    IN_ORDER_TO = "in_order_to"              # "in order to", "to" (purpose)
    DESIGNED_TO = "designed_to"              # "designed to", "evolved to"
    FOR_THE_PURPOSE = "for_the_purpose"      # "for the purpose of", "serves to"
    SO_THAT = "so_that"                      # "so that", "in order that"
    FUNCTIONAL_IMPLICATION = "functional"     # "function of X is to"
    AGENTIC_LANGUAGE = "agentic"             # "cells choose", "systems decide"


@dataclass
class TeleologyAlert:
    """A detected instance of teleological framing"""
    teleology_type: TeleologyType
    location: str  # Surrounding text context
    problematic_phrase: str
    suggested_reframing: str
    confidence: float  # How confident this is teleological
    explanation: str  # Why this is problematic


class TeleologyPatterns:
    """
    Patterns that indicate teleological framing.

    LESSON from bacterial cell cycle review:
    - "in order to" implies purpose where none exists
    - "designed to" suggests intelligent design
    - "evolved to" implies foresight (evolution doesn't have goals)
    - "serves to" implies function as purpose
    """

    TELEOLOGICAL_PATTERNS = {
        TeleologyType.IN_ORDER_TO: [
            r'in order to',
            r'\bin order that\b',
            r'\bto\s+(?:achieve|accomplish|attain|ensure|guarantee|maximize|minimize)\b'
        ],
        TeleologyType.DESIGNED_TO: [
            r'\bdesigned to\b',
            r'\bevolved to\b',
            r'\badapted to\b',
            r'\bselected for\b'
        ],
        TeleologyType.FOR_THE_PURPOSE: [
            r'\bfor the purpose of\b',
            r'\bwith the purpose of\b',
            r'\bintended to\b',
            r'\bmeant to\b',
            r'\bmeant for\b'
        ],
        TeleologyType.SO_THAT: [
            r'\bso that\b',
            r'\bin order that\b',
            r'\bwith the aim of\b'
        ],
        TeleologyType.FUNCTIONAL_IMPLICATION: [
            r'\bfunction of\b.*?\bto\b',
            r'\brole of\b.*?\bto\b',
            r'\bjob of\b.*?\bto\b',
            r'\bpurpose of\b.*?\bto\b'
        ],
        TeleologyType.AGENTIC_LANGUAGE: [
            r'\bcells?\s+(?:choose|decide|prefer|want|need|try)\b',
            r'\bsystems?\s+(?:decide|choose|prefer)\b',
            r'\borganisms?\s+(?:choose|decide|prefer|want)\b'
        ]
    }

    MECHANISTIC_ALTERNATIVES = {
        "in order to": "which results in",
        "designed to": "that functions to",
        "evolved to": "evolved such that",
        "for the purpose of": "contributing to",
        "so that": "such that",
        "serves to": "functions to",
        "function of X is to": "X functions by",
        "cells choose": "cells exhibit differential",
        "systems decide": "systems exhibit",
        "intended to": "that results in"
    }


class TeleologyDetector:
    """
    Detect teleological framing in scientific text.

    CHALLENGE: Some "purpose-like" language is legitimate functional description.
    - LEGITIMATE: "The function of hemoglobin is to carry oxygen"
    - PROBLEMATIC: "Hemoglobin evolved in order to carry oxygen"

    DISTINCTION: Current function vs evolutionary purpose.
    """

    def __init__(self):
        self.patterns = TeleologyPatterns()
        self.alerts: List[TeleologyAlert] = []

    def detect_teleology(self, text: str) -> List[TeleologyAlert]:
        """
        Detect all instances of teleological framing in text.

        Returns list of alerts with suggested reframing.
        """
        alerts = []
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check each teleology type
            for tel_type, patterns in self.patterns.TELEOLOGICAL_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        alert = self._create_alert(tel_type, sentence, match.group(), match.start())
                        if alert:
                            alerts.append(alert)

        self.alerts = alerts
        return alerts

    def _create_alert(
        self,
        tel_type: TeleologyType,
        sentence: str,
        phrase: str,
        position: int
    ) -> Optional[TeleologyAlert]:
        """Create a teleology alert with context and suggestion"""
        # Check for exceptions (legitimate functional description)
        if self._is_legitimate_functional_description(sentence):
            return None

        # Generate suggestion
        suggestion = self._generate_reframing(sentence, phrase, tel_type)

        # Generate explanation
        explanation = self._generate_explanation(tel_type, phrase)

        # Get context (surrounding text)
        context_start = max(0, position - 30)
        context_end = min(len(sentence), position + len(phrase) + 30)
        context = sentence[context_start:context_end]

        return TeleologyAlert(
            teleology_type=tel_type,
            location=context,
            problematic_phrase=phrase,
            suggested_reframing=suggestion,
            confidence=self._calculate_confidence(tel_type, sentence),
            explanation=explanation
        )

    def _is_legitimate_functional_description(self, sentence: str) -> bool:
        """
        Check if this is a legitimate functional description.

        EXCEPTIONS:
        - "The function of X is Y" (current function, not evolutionary purpose)
        - "X plays a role in Y" (mechanistic description)
        - "X contributes to Y" (contribution, not purpose)
        """
        sentence_lower = sentence.lower()

        # Legitimate patterns
        legitimate_patterns = [
            r'\bfunction of\b.*?\bis\b(?:\s+(?:called|named|termed))?\s+(?:(?!to\b)\w+)',
            r'\brole of\b.*?\sis\b',
            r'\bcontributes to\b',
            r'\bplays?\s+a\s+role\b'
        ]

        for pattern in legitimate_patterns:
            if re.search(pattern, sentence_lower):
                return True

        return False

    def _generate_reframing(
        self,
        sentence: str,
        phrase: str,
        tel_type: TeleologyType
    ) -> str:
        """Generate mechanistic reframing for teleological phrase"""
        # Get mapping
        alternatives = self.patterns.MECHANISTIC_ALTERNATIVES

        # Find appropriate alternative
        for key, alternative in alternatives.items():
            if key in phrase.lower():
                # Simple replacement
                reframed = re.sub(
                    re.escape(key),
                    alternative,
                    sentence,
                    flags=re.IGNORECASE
                )
                return reframed

        # Fallback: remove teleological language
        if tel_type == TeleologyType.IN_ORDER_TO:
            return sentence.replace(phrase, "which results in")
        elif tel_type == TeleologyType.DESIGNED_TO:
            return sentence.replace(phrase, "that functions to")
        elif tel_type == TeleologyType.FOR_THE_PURPOSE:
            return sentence.replace(phrase, "contributing to")
        elif tel_type == TeleologyType.SO_THAT:
            return sentence.replace(phrase, "such that")

        return f"[Remove '{phrase}' and rephrase mechanistically]"

    def _generate_explanation(self, tel_type: TeleologyType, phrase: str) -> str:
        """Generate explanation of why this is problematic"""
        explanations = {
            TeleologyType.IN_ORDER_TO: f"'{phrase}' implies purpose where none exists. "
                                       f"Processes don't occur 'in order to' achieve outcomes; "
                                       f"they occur, and outcomes result.",
            TeleologyType.DESIGNED_TO: f"'{phrase}' suggests intelligent design or foresight. "
                                      f"Evolution doesn't design; it selects from variation.",
            TeleologyType.FOR_THE_PURPOSE: f"'{phrase}' attributes purpose to natural processes. "
                                           f"Use mechanistic or functional language instead.",
            TeleologyType.SO_THAT: f"'{phrase}' implies intentionality. "
                                  f"Use 'such that' for causal relationships.",
            TeleologyType.FUNCTIONAL_IMPLICATION: f"Careful with function statements. "
                                                 f"Distinguish current function from evolutionary origin.",
            TeleologyType.AGENTIC_LANGUAGE: f"Cells and systems don't have agency. "
                                           f"They exhibit behaviors, they don't 'choose' or 'decide'."
        }
        return explanations.get(tel_type, "Teleological framing detected")

    def _calculate_confidence(self, tel_type: TeleologyType, sentence: str) -> float:
        """Calculate confidence that this is truly teleological"""
        base_confidence = 0.7

        # Increase confidence if multiple teleological markers present
        tel_count = sum(1 for patterns in self.patterns.TELEOLOGICAL_PATTERNS.values()
                       for pattern in patterns
                       if re.search(pattern, sentence, re.IGNORECASE))

        confidence = base_confidence + (tel_count - 1) * 0.1
        return min(0.95, confidence)

    def filter_text(self, text: str) -> Tuple[str, List[TeleologyAlert]]:
        """
        Filter text to remove teleological framing.

        Returns: (filtered_text, alerts)
        """
        alerts = self.detect_teleology(text)
        filtered_text = text

        # Apply replacements (reverse order to preserve positions)
        for alert in sorted(alerts, key=lambda a: a.location.count(' '), reverse=True):
            filtered_text = filtered_text.replace(alert.problematic_phrase, alert.suggested_reframing)

        return filtered_text, alerts


class TeleologyFilter:
    """
    Main interface for teleology filtering.

    USAGE:
        filter = TeleologyFilter()
        alerts = filter.check(text)
        filtered, alerts = filter.filter_text(text)
    """

    def __init__(self):
        self.detector = TeleologyDetector()

    def check(self, text: str) -> List[TeleologyAlert]:
        """Check text for teleological framing"""
        return self.detector.detect_teleology(text)

    def filter_text(self, text: str) -> Tuple[str, List[TeleologyAlert]]:
        """Filter text to remove teleological framing"""
        return self.detector.filter_text(text)

    def get_summary(self, alerts: List[TeleologyAlert]) -> Dict[str, Any]:
        """Get summary of teleology detected"""
        if not alerts:
            return {
                'total_alerts': 0,
                'severity': 'none',
                'types': {},
                'recommendation': 'No teleological framing detected.'
            }

        # Count by type
        type_counts = {}
        for alert in alerts:
            tel_type = alert.teleology_type.value
            type_counts[tel_type] = type_counts.get(tel_type, 0) + 1

        # Determine overall severity
        high_confidence = sum(1 for a in alerts if a.confidence > 0.8)
        severity = 'high' if high_confidence > len(alerts) / 2 else 'medium'

        recommendation = self._generate_recommendation(alerts)

        return {
            'total_alerts': len(alerts),
            'severity': severity,
            'types': type_counts,
            'high_confidence_count': high_confidence,
            'recommendation': recommendation
        }

    def _generate_recommendation(self, alerts: List[TeleologyAlert]) -> str:
        """Generate recommendation based on alerts"""
        if len(alerts) == 0:
            return "No teleological framing detected."

        high_conf = sum(1 for a in alerts if a.confidence > 0.8)
        total = len(alerts)

        if high_conf > total / 2:
            return f"High-confidence teleological framing detected ({high_conf}/{total} instances). "
                   f"Strongly recommend mechanistic reframing before submission."
        else:
            return f"Some teleological framing detected ({total} instances). "
                   f"Review and consider mechanistic reframing."


def create_teleology_filter() -> TeleologyFilter:
    """Factory function to create teleology filter"""
    return TeleologyFilter()


# Singleton instance
_instance = None

def get_teleology_filter() -> TeleologyFilter:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = create_teleology_filter()
    return _instance
