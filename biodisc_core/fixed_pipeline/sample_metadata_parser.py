"""P0.3 (Defect C) — Derive real experimental groups from sample metadata.

Previously the downloaders FABRICATED case/control assignment
(``[0]*(n//2)+[1]*(n-n//2)`` or ``[i%2]``), which makes every differential-
expression result statistical noise even when expression values are real.

This module parses ``!Sample_*`` metadata from a GEO series-matrix text and
derives a binary group assignment from a real sample characteristic. If no
determinable binary grouping exists it returns ``None`` — the caller must then
REJECT the dataset rather than fabricate labels.

This module NEVER fabricates groups. Returning ``None`` is the correct, honest
outcome when the experimental design cannot be recovered.
"""
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GroupAssignment:
    """A derived binary group assignment for the samples in a dataset."""
    labels: np.ndarray          # int array of 0/1, one per sample
    field: str                  # the characteristic used (e.g. 'treatment')
    values_map: Dict[int, str]  # label -> the raw characteristic value
    source: str                 # metadata line family, e.g. 'characteristics'
    confidence: float           # heuristic confidence in the assignment [0,1]


def _split_sample_line(line: str) -> tuple[str, List[str]]:
    """Split a '!Sample_field<sep>v1<TAB>v2...' line into (field, [values]).

    Handles both ``!Field = v1\\tv2`` and ``!Field\\tv1\\tv2`` forms, and strips
    surrounding quotes from each value.
    """
    # Strip leading '!' and the optional '= ' separator after the field name.
    body = line.lstrip()
    if body.startswith('!'):
        body = body[1:]
    # The field name runs up to the first tab or the first ' = '.
    if '=' in body and ('\t' not in body.split('=', 1)[0]):
        field_part, vals_part = body.split('=', 1)
    else:
        # first token (up to first tab) is the field name
        first_tab = body.find('\t')
        if first_tab == -1:
            return body.strip(), []
        field_part, vals_part = body[:first_tab], body[first_tab + 1:]
    field = field_part.strip()
    raw_values = [v.strip().strip('"').strip("'") for v in vals_part.split('\t')]
    return field, raw_values


def _characteristic_key(value: str) -> str:
    """Extract the 'key' from a 'key: value' characteristic cell.

    Returns '' if the cell is not in key: value form.
    """
    if ':' in value:
        return value.split(':', 1)[0].strip().lower()
    return ''


def parse_groups_from_series_matrix(
    matrix_text: str,
    question: Optional[str] = None,
) -> Optional[GroupAssignment]:
    """Derive a binary group assignment from GEO series-matrix sample metadata.

    Args:
        matrix_text: The full (decompressed) GEO series matrix text, including
            ``!Sample_*`` header lines.
        question: Optional biological question, used to prefer grouping fields
            whose values relate to the question (keyword overlap).

    Returns:
        A GroupAssignment if a binary grouping is recoverable, else None.
    """
    if not matrix_text:
        return None

    # Collect per-characteristic value vectors across samples.
    # characteristics[field] = list of per-sample values (one vector per
    # occurrence of that !Sample_characteristics_ch1 line).
    characteristics: Dict[str, List[List[str]]] = {}
    sample_count = 0

    for line in matrix_text.split('\n'):
        line = line.rstrip('\r')
        if not line.startswith('!Sample_'):
            continue
        field, values = _split_sample_line(line)
        if not values:
            continue
        sample_count = max(sample_count, len(values))
        characteristics.setdefault(field, []).append(values)

    if sample_count < 2 or not characteristics:
        return None

    # Build candidate binary fields. Each candidate is (field, key, [values]).
    # Identifier fields (e.g. Sample_geo_accession) are unique per sample and are
    # NEVER a valid experimental grouping — exclude them. Likewise exclude
    # TECHNICAL fields (dates, batch/plate/well, channel) that can be binary but
    # are not biological case/control (otherwise the parser would group samples
    # by submission date, producing a meaningless DE).
    IDENTIFIER_HINTS = ('accession', 'sample_id', 'geo_accession')
    NON_BIOLOGICAL_HINTS = (
        'submission_date', 'scan_date', 'extract_id', 'hyb_date', 'hybridization',
        'array_id', 'array_batch', 'batch', 'plate', 'well', 'channel',
        'label_protocol', 'scan_protocol', 'data_processing',
    )
    candidates: List[tuple] = []
    for field, vectors in characteristics.items():
        field_l = field.lower()
        if any(h in field_l for h in IDENTIFIER_HINTS):
            continue
        if any(h in field_l for h in NON_BIOLOGICAL_HINTS):
            continue
        for vec in vectors:
            if len(vec) != sample_count:
                continue
            distinct = set(vec)
            if len(distinct) == 2 and '' not in distinct:
                key = _characteristic_key(vec[0]) or field
                candidates.append((field, key, vec))

    if not candidates:
        logger.info(
            "   No binary sample characteristic found; cannot determine groups"
        )
        return None

    # Prefer candidates whose key/values overlap the question keywords.
    q_words = set(re.findall(r'[a-z]{3,}', (question or '').lower()))

    def _score(cand: tuple) -> tuple:
        field, key, vec = cand
        overlap = 0
        if q_words:
            text_blob = f"{field} {key} " + " ".join(vec).lower()
            overlap = sum(1 for w in q_words if w in text_blob)
        # Prefer balanced groups, then question overlap.
        n1 = sum(1 for v in vec if v == vec[0])
        balance = 1.0 - abs(n1 - len(vec) / 2) / (len(vec) / 2)
        return (overlap, balance)

    candidates.sort(key=_score, reverse=True)
    field, key, vec = candidates[0]

    v_a, v_b = sorted(set(vec))
    labels = np.array([0 if v == v_a else 1 for v in vec], dtype=int)

    confidence = 0.5
    if q_words and _score(candidates[0])[0] > 0:
        confidence = 0.8
    # Slightly penalize unbalanced splits.
    n1 = int((labels == 0).sum())
    balance = 1.0 - abs(n1 - len(vec) / 2) / (len(vec) / 2)
    confidence = round(min(1.0, confidence * (0.6 + 0.4 * balance)), 3)

    logger.info(
        f"   Derived groups from '{key}' ({field}): "
        f"{int((labels == 0).sum())} vs {int((labels == 1).sum())} "
        f"(confidence={confidence})"
    )

    return GroupAssignment(
        labels=labels,
        field=key,
        values_map={0: v_a, 1: v_b},
        source='characteristics',
        confidence=confidence,
    )
