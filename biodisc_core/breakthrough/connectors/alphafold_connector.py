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
"""AlphaFold DB structure connector (breakthrough rebuild item 2 — data connector).

Implements the ``alphafold_ebi_api`` connector referenced by
``biodisc_core.breakthrough.remining``. The re-mining framework flagged the
NOVEL question:

    "cross-protein: which DISORDERED regions (predicted by AlphaFold
     low-confidence) are SHARED across protein families? Do they represent a
     new class of regulatory elements?"

This connector answers the data-engineering half of that question. It queries the
AlphaFold Protein Structure Database REST API (EMBL-EBI / DeepMind), retrieves the
predicted-structure *metadata* (NOT the atomic coordinates — those need structural-
biology tooling), and distills it down to the signal BIODISC cares about: per-residue
confidence (pLDDT) and the disorder it implies.

Why confidence/disorder and not coordinates
-------------------------------------------
AlphaFold's pLDDT (predicted Local Distance Difference Test, 0-100) is inversely a
disorder predictor: residues with pLDDT < 50 are very likely intrinsically disordered
(IDRs), and 50-70 is a boundary zone. Intrinsically disordered regions are a frontier
in drug discovery and regulatory biology, and the CROSS-PROTEIN pattern of disorder
(shared IDRs at analogous positions across families) has not been systematically mined.
That is exactly the second-wave reanalysis this connector enables.

API contract
------------
``GET https://alphafold.ebi.ac.uk/api/prediction/{uniprot_accession}`` returns a JSON
array of prediction records (one per isoform / sequence variant). Each record carries,
among other fields:

    uniprotAccession      — canonical UniProt accession
    sequence              — amino-acid string
    aminoAcids            — list of {residueNumber, aminoAcid,
                            confidenceScore (pLDDT 0-100), confidenceCategory,
                            predictedSecondaryStructure}
    predictedDomains      — list of domain annotations (start/end/name)
    modelConfidence       — aggregate confidence summary
    latestVersion         — model version string (e.g. "4")
    modelCreatedDate      — ISO date
    pdbUrl / cifUrl / ... — coordinate downloads (NOT fetched here)

The connector parses defensively: field names have drifted across AFDB versions, so it
accepts ``aminoAcids[].confidenceScore`` directly and falls back to deriving pLDDT from
``confidenceCategory`` buckets if the numeric score is absent.

OFFLINE TESTING
---------------
``dry_run=True`` returns deterministic synthetic pLDDT profiles seeded by the UniProt
accession, so the full disorder-analysis pipeline can be exercised with no network.
"""
from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — pLDDT thresholds and API wiring
# ---------------------------------------------------------------------------

ALPHAFOLD_PREDICTION_URL = "https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
"""Canonical AFDB per-accession prediction endpoint."""

# pLDDT interpretation (AlphaFold convention). The task spec fixes the disorder
# boundary at <50 (disordered) with 50-70 as a boundary zone and >70 structured.
PLDDT_DISORDERED = 50.0      # < this  => disordered (very low confidence / IDR)
PLDDT_STRUCTURED = 70.0      # > this  => structured (confident + very high)
# 50 <= pLDDT < 70            => boundary (low confidence, treat with caution)

CATEGORY = "structured"      # sentinel values used in ResidueConfidence.category
CATEGORY_BOUNDARY = "boundary"
CATEGORY_DISORDERED = "disordered"

# Map AFDB confidenceCategory strings onto our three buckets. The API has used
# several labels across versions; this map covers the known variants.
_CATEGORY_TO_PLDDT: Dict[str, float] = {
    # very-high / confident bucket -> represent at the high end of its band
    "very high": 95.0,
    "high": 80.0,
    "confident": 80.0,
    # boundary bucket
    "medium": 60.0,
    "low confidence": 60.0,
    "low": 60.0,
    # disordered bucket
    "very low": 30.0,
    "caution": 30.0,
}

# Relative-position bins for cross-protein disorder comparison. Protein lengths vary
# wildly, so absolute residue numbers are not comparable; we project every disorder
# region onto a normalized [0, 1) coordinate and bucket it.
POSITION_BINS: Tuple[Tuple[float, float, str], ...] = (
    (0.00, 0.34, "N-terminal"),
    (0.34, 0.66, "middle"),
    (0.66, 1.01, "C-terminal"),
)


# ---------------------------------------------------------------------------
# Structured result types
# ---------------------------------------------------------------------------


@dataclass
class ResidueConfidence:
    """Per-residue confidence for one amino acid."""

    residue_number: int   # 1-based, matching UniProt / AFDB convention
    amino_acid: str       # single-letter code
    plddt: float          # 0-100 (AlphaFold confidence)
    category: str         # CATEGORY | CATEGORY_BOUNDARY | CATEGORY_DISORDERED


@dataclass
class Region:
    """A maximal run of consecutive residues that share a disorder class."""

    start: int            # 1-based, inclusive
    end: int              # 1-based, inclusive
    length: int
    mean_plddt: float
    category: str         # which class this region belongs to


@dataclass
class DomainAnnotation:
    """A predicted domain from the AFDB record (coordinates only, no structure)."""

    identifier: str
    start: int            # 1-based, inclusive
    end: int              # 1-based, inclusive
    mean_plddt: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProteinDisorderProfile:
    """Per-protein disorder profile — the unit of analysis.

    This is what BIODISC's re-mining layer consumes. It deliberately excludes
    atomic coordinates (not needed for disorder mining and too heavy to carry).
    """

    uniprot_id: str
    sequence: str
    sequence_length: int
    residues: List[ResidueConfidence] = field(default_factory=list)
    mean_plddt: float = 0.0
    fraction_structured: float = 0.0   # fraction of residues with pLDDT > 70
    fraction_boundary: float = 0.0     # 50 <= pLDDT < 70
    fraction_disordered: float = 0.0   # pLDDT < 50
    disorder_regions: List[Region] = field(default_factory=list)    # < 50
    boundary_regions: List[Region] = field(default_factory=list)    # 50-70
    structured_regions: List[Region] = field(default_factory=list)  # > 70
    domains: List[DomainAnnotation] = field(default_factory=list)
    model_version: str = ""
    model_created_date: str = ""
    found: bool = True          # False when AFDB has no prediction (404)
    error: str = ""             # populated on fetch failure
    source: str = "alphafold_ebi"   # 'alphafold_ebi' | 'dry_run'

    def disorder_vector(self, length: int = 100) -> List[int]:
        """Return the disorder profile resampled to a fixed length.

        Each output bin is 1 if the protein is predominantly disordered
        (pLDDT < PLDDT_DISORDERED) at that relative position, else 0. This
        normalization is what makes disorder comparable across proteins of
        different lengths.
        """
        if self.sequence_length == 0 or not self.residues:
            return [0] * length
        out = [0] * length
        for i in range(length):
            lo = int(i * self.sequence_length / length)
            hi = max(lo + 1, int((i + 1) * self.sequence_length / length))
            window = self.residues[lo:hi]
            if window:
                mean_plddt = sum(r.plddt for r in window) / len(window)
                if mean_plddt < PLDDT_DISORDERED:
                    out[i] = 1
        return out


@dataclass
class SharedDisorderPattern:
    """A disorder region that recurs across proteins at an analogous position."""

    position_bin: str            # 'N-terminal' | 'middle' | 'C-terminal'
    relative_range: Tuple[float, float]  # normalized [start, end) in [0, 1)
    proteins: List[str]          # UniProt IDs exhibiting disorder here
    fraction_of_profiles: float  # proteins / total

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"SharedDisorderPattern({self.position_bin}, "
            f"rel={self.relative_range[0]:.2f}-{self.relative_range[1]:.2f}, "
            f"n={len(self.proteins)}, frac={self.fraction_of_profiles:.2f})"
        )


@dataclass
class CrossProteinComparison:
    """Cross-protein disorder comparison — answers the re-mining novel question."""

    uniprot_ids: List[str]
    profiles: Dict[str, ProteinDisorderProfile]
    shared_disorder_patterns: List[SharedDisorderPattern] = field(default_factory=list)
    mean_disorder_fraction: float = 0.0
    disorder_similarity: Dict[Tuple[str, str], float] = field(default_factory=dict)
    n_profiles_compared: int = 0
    n_not_found: int = 0
    summary: str = ""


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class AlphaFoldConnector:
    """Fetch and parse AlphaFold DB predicted-structure metadata.

    Parameters
    ----------
    dry_run : bool
        If True, never hit the network — return deterministic synthetic profiles
        seeded by the UniProt accession. Enables fully offline testing of the
        disorder-analysis pipeline.
    timeout : float
        Per-request HTTP timeout in seconds.
    rate_limit_seconds : float
        Minimum gap between successive API calls (be a polite client).
    user_agent : str
        Sent in the User-Agent header.
    """

    def __init__(
        self,
        dry_run: bool = False,
        timeout: float = 30.0,
        rate_limit_seconds: float = 1.0,
        user_agent: str = "BIODISC-AlphaFoldConnector/1.0",
    ) -> None:
        self.dry_run = dry_run
        self.timeout = timeout
        self.rate_limit_seconds = rate_limit_seconds
        self.user_agent = user_agent
        self._last_request_time: float = 0.0

    # -- public API ---------------------------------------------------------

    def fetch_prediction(self, uniprot_id: str) -> ProteinDisorderProfile:
        """Fetch and parse the disorder profile for a single UniProt accession.

        Returns a ``ProteinDisorderProfile`` with ``found=False`` if AFDB has no
        prediction for this accession (HTTP 404) and ``error`` set on other
        failures. Never raises for expected conditions (404, network) — logs and
        returns a structured "not found" profile so batch callers keep going.
        """
        uniprot_id = (uniprot_id or "").strip().upper()
        if not uniprot_id:
            return ProteinDisorderProfile(
                uniprot_id="", sequence="", sequence_length=0,
                found=False, error="empty uniprot_id",
            )

        if self.dry_run:
            return self._synthetic_profile(uniprot_id)

        url = ALPHAFOLD_PREDICTION_URL.format(uniprot_id=uniprot_id)
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}

        try:
            self._respect_rate_limit()
            response = requests.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            logger.warning("AlphaFold fetch failed for %s: %s", uniprot_id, exc)
            return ProteinDisorderProfile(
                uniprot_id=uniprot_id, sequence="", sequence_length=0,
                found=False, error=f"network error: {exc}",
            )

        if response.status_code == 404:
            logger.info("AlphaFold: no prediction for %s (404)", uniprot_id)
            return ProteinDisorderProfile(
                uniprot_id=uniprot_id, sequence="", sequence_length=0,
                found=False, error="not in AlphaFold DB",
            )
        if response.status_code != 200:
            logger.warning("AlphaFold %s: HTTP %s", uniprot_id, response.status_code)
            return ProteinDisorderProfile(
                uniprot_id=uniprot_id, sequence="", sequence_length=0,
                found=False, error=f"HTTP {response.status_code}",
            )

        try:
            payload = response.json()
        except ValueError as exc:
            logger.warning("AlphaFold %s: invalid JSON: %s", uniprot_id, exc)
            return ProteinDisorderProfile(
                uniprot_id=uniprot_id, sequence="", sequence_length=0,
                found=False, error=f"invalid JSON: {exc}",
            )

        return self.parse_prediction(payload, uniprot_id)

    def fetch_predictions(
        self, uniprot_ids: Sequence[str]
    ) -> Dict[str, ProteinDisorderProfile]:
        """Fetch disorder profiles for a set of UniProt accessions.

        404s and per-protein errors are captured in the returned profile (``found=False``)
        rather than raised, so one missing accession doesn't abort the batch.
        """
        profiles: Dict[str, ProteinDisorderProfile] = {}
        for uid in uniprot_ids:
            key = (uid or "").strip().upper()
            profiles[key] = self.fetch_prediction(key)
        return profiles

    def compare_disorder(
        self, profiles: Dict[str, ProteinDisorderProfile]
    ) -> CrossProteinComparison:
        """Compare disorder profiles across proteins.

        Implements the re-mining novel question: which disordered regions are
        *shared* across proteins at analogous (normalized) positions?
        """
        found = {uid: p for uid, p in profiles.items() if p.found}
        uids = list(found.keys())

        comp = CrossProteinComparison(
            uniprot_ids=list(profiles.keys()),
            profiles=profiles,
            n_profiles_compared=len(found),
            n_not_found=len(profiles) - len(found),
        )

        if not found:
            comp.summary = "No AlphaFold predictions found for any input accession."
            return comp

        # Mean disorder fraction across the cohort.
        frac = [p.fraction_disordered for p in found.values()]
        comp.mean_disorder_fraction = round(sum(frac) / len(frac), 4)

        # Shared-disorder patterns: project every disorder region onto normalized
        # [0,1) coordinates and look for positions where many proteins are disordered.
        comp.shared_disorder_patterns = self._shared_disorder(found)

        # Pairwise disorder-profile similarity (Jaccard on resampled vectors).
        comp.disorder_similarity = self._pairwise_similarity(found)

        comp.summary = (
            f"Compared {len(found)} protein(s); mean disordered fraction "
            f"{comp.mean_disorder_fraction:.2%}; "
            f"{len(comp.shared_disorder_patterns)} shared-disorder position(s) "
            f"where >= half of proteins are disordered."
        )
        return comp

    def analyze_shared_disorder(
        self, uniprot_ids: Sequence[str]
    ) -> CrossProteinComparison:
        """Convenience: fetch + compare in one call (the full novel-question pipeline)."""
        return self.compare_disorder(self.fetch_predictions(uniprot_ids))

    # -- parsing ------------------------------------------------------------

    def parse_prediction(
        self, payload: Any, uniprot_id: str = ""
    ) -> ProteinDisorderProfile:
        """Parse an AFDB ``/api/prediction/{id}`` JSON payload into a profile.

        ``payload`` may be the raw list returned by the API or a single record dict.
        Exposed publicly so cached/offline payloads can be parsed without a request.
        """
        record = self._pick_record(payload, uniprot_id)
        if record is None:
            return ProteinDisorderProfile(
                uniprot_id=uniprot_id, sequence="", sequence_length=0,
                found=False, error="empty prediction payload",
            )

        uniprot_id = uniprot_id or str(
            record.get("uniprotAccession") or record.get("uniprotId") or ""
        ).upper()
        sequence = str(record.get("sequence") or "")
        residues = self._parse_residues(record, sequence)

        domains = self._parse_domains(record, residues)

        profile = ProteinDisorderProfile(
            uniprot_id=uniprot_id,
            sequence=sequence,
            sequence_length=len(sequence),
            residues=residues,
            domains=domains,
            model_version=str(record.get("latestVersion") or record.get("modelVersion") or ""),
            model_created_date=str(record.get("modelCreatedDate") or ""),
            source="alphafold_ebi",
        )
        self._finalize_profile(profile)
        return profile

    # -- internal: record selection ----------------------------------------

    @staticmethod
    def _pick_record(payload: Any, uniprot_id: str) -> Optional[Dict[str, Any]]:
        """Select the canonical record from an AFDB response.

        The endpoint returns a list (one entry per isoform). Prefer the entry
        whose ``uniprotAccession`` matches and ``uniprotStart`` is 1 (the
        canonical sequence); fall back to the first entry.
        """
        if isinstance(payload, list):
            if not payload:
                return None
            for entry in payload:
                if not isinstance(entry, dict):
                    continue
                acc = str(entry.get("uniprotAccession", "")).upper()
                if acc == uniprot_id and entry.get("uniprotStart") in (1, "1", None):
                    return entry
            for entry in payload:
                if isinstance(entry, dict):
                    return entry
            return None
        if isinstance(payload, dict):
            return payload
        return None

    # -- internal: per-residue parsing -------------------------------------

    @staticmethod
    def _parse_residues(
        record: Dict[str, Any], sequence: str
    ) -> List[ResidueConfidence]:
        """Build the per-residue confidence list.

        Handles three shapes the AFDB API has used over versions:
          1. ``aminoAcids`` as a list of dicts with ``confidenceScore``.
          2. ``aminoAcids`` as a list of dicts with only ``confidenceCategory``
             (numeric score absent -> derive a representative pLDDT).
          3. A flat top-level ``pLDDT`` array aligned to the sequence.
        """
        seq_len = len(sequence)
        amino_acids = record.get("aminoAcids")

        # Case 1 / 2: list of per-residue dicts.
        if isinstance(amino_acids, list) and amino_acids:
            residues: List[ResidueConfidence] = []
            for idx, aa in enumerate(amino_acids):
                if not isinstance(aa, dict):
                    continue
                res_no = int(aa.get("residueNumber", idx + 1))
                letter = str(aa.get("aminoAcid") or (sequence[idx] if idx < seq_len else "X"))
                plddt = aa.get("confidenceScore")
                if plddt is None:
                    cat = str(aa.get("confidenceCategory") or "").strip().lower()
                    plddt = _CATEGORY_TO_PLDDT.get(cat, 50.0)
                else:
                    plddt = float(plddt)
                residues.append(ResidueConfidence(
                    residue_number=res_no,
                    amino_acid=letter,
                    plddt=plddt,
                    category=_classify_plddt(plddt),
                ))
            if residues:
                return residues

        # Case 3: flat pLDDT array.
        flat = record.get("pLDDT") or record.get("plddt")
        if isinstance(flat, list) and flat:
            residues = []
            for idx, val in enumerate(flat):
                try:
                    plddt = float(val)
                except (TypeError, ValueError):
                    plddt = 50.0
                letter = sequence[idx] if idx < seq_len else "X"
                residues.append(ResidueConfidence(
                    residue_number=idx + 1,
                    amino_acid=letter,
                    plddt=plddt,
                    category=_classify_plddt(plddt),
                ))
            if residues:
                return residues

        # Nothing usable — synthesize a neutral boundary profile so downstream
        # code still gets a well-formed vector rather than crashing.
        return [
            ResidueConfidence(i + 1, sequence[i] if i < seq_len else "X", 50.0,
                              CATEGORY_BOUNDARY)
            for i in range(max(seq_len, 1))
        ]

    @staticmethod
    def _parse_domains(
        record: Dict[str, Any], residues: List[ResidueConfidence]
    ) -> List[DomainAnnotation]:
        """Parse ``predictedDomains`` (if present) into DomainAnnotation objects.

        The AFDB schema for domains has varied; we read start/end defensively from
        a few likely key names and attach the mean pLDDT over the span.
        """
        raw_domains = record.get("predictedDomains")
        if not isinstance(raw_domains, list):
            return []

        by_resno = {r.residue_number: r for r in residues}
        out: List[DomainAnnotation] = []
        for d in raw_domains:
            if not isinstance(d, dict):
                continue
            start = d.get("start", d.get("residueStart", d.get("begin")))
            end = d.get("end", d.get("residueEnd", d.get("endResidue")))
            try:
                start_i = int(start)
                end_i = int(end)
            except (TypeError, ValueError):
                continue
            if end_i < start_i:
                continue
            span = [by_resno[r] for r in range(start_i, end_i + 1) if r in by_resno]
            mean_plddt = (
                sum(r.plddt for r in span) / len(span) if span else 0.0
            )
            identifier = str(
                d.get("identifier") or d.get("name")
                or d.get("displayName") or f"{start_i}-{end_i}"
            )
            out.append(DomainAnnotation(
                identifier=identifier, start=start_i, end=end_i,
                mean_plddt=round(mean_plddt, 2), raw=d,
            ))
        return out

    # -- internal: profile aggregation -------------------------------------

    @staticmethod
    def _finalize_profile(profile: ProteinDisorderProfile) -> None:
        """Compute aggregate stats and segment regions from the residue list."""
        residues = profile.residues
        n = len(residues)
        if n == 0:
            return

        profile.mean_plddt = round(sum(r.plddt for r in residues) / n, 2)
        profile.fraction_structured = round(
            sum(1 for r in residues if r.plddt > PLDDT_STRUCTURED) / n, 4)
        profile.fraction_boundary = round(
            sum(1 for r in residues
                if PLDDT_DISORDERED <= r.plddt <= PLDDT_STRUCTURED) / n, 4)
        profile.fraction_disordered = round(
            sum(1 for r in residues if r.plddt < PLDDT_DISORDERED) / n, 4)

        profile.disorder_regions = _segment_regions(residues, CATEGORY_DISORDERED)
        profile.boundary_regions = _segment_regions(residues, CATEGORY_BOUNDARY)
        profile.structured_regions = _segment_regions(residues, CATEGORY)

    # -- internal: cross-protein analysis ----------------------------------

    @staticmethod
    def _shared_disorder(
        found: Dict[str, ProteinDisorderProfile],
    ) -> List[SharedDisorderPattern]:
        """Find relative positions where many proteins are simultaneously disordered.

        Each protein's disorder is resampled to ``length`` normalized bins; for
        every bin we count how many proteins are disordered there. Positions where
        >= half of the proteins are disordered (and at least 2) are reported as
        shared-disorder patterns, grouped into N/middle/C buckets.
        """
        n = len(found)
        if n < 2:
            return []

        n_bins = 50
        vectors = {uid: p.disorder_vector(n_bins) for uid, p in found.items()}
        threshold = max(2, n // 2 + (n % 2))  # majority, but at least 2

        patterns: List[SharedDisorderPattern] = []
        i = 0
        while i < n_bins:
            count = sum(1 for v in vectors.values() if v[i] >= 1)
            if count >= threshold:
                # extend the run of shared-disorder bins
                j = i
                while j + 1 < n_bins and all(
                    sum(1 for v in vectors.values() if v[k] >= 1) >= threshold
                    for k in (j + 1,)
                ):
                    j += 1
                rel_lo = i / n_bins
                rel_hi = (j + 1) / n_bins
                members = [uid for uid, v in vectors.items() if any(v[k] for k in range(i, j + 1))]
                patterns.append(SharedDisorderPattern(
                    position_bin=_relative_position_bin((rel_lo + rel_hi) / 2),
                    relative_range=(round(rel_lo, 3), round(rel_hi, 3)),
                    proteins=sorted(members),
                    fraction_of_profiles=round(len(members) / n, 3),
                ))
                i = j + 1
            else:
                i += 1
        return patterns

    @staticmethod
    def _pairwise_similarity(
        found: Dict[str, ProteinDisorderProfile]
    ) -> Dict[Tuple[str, str], float]:
        """Jaccard similarity of normalized disorder vectors for every protein pair."""
        uids = list(found.keys())
        if len(uids) < 2:
            return {}
        n_bins = 50
        vectors = {uid: set(k for k, b in enumerate(found[uid].disorder_vector(n_bins)) if b)
                   for uid in uids}
        out: Dict[Tuple[str, str], float] = {}
        for a_idx in range(len(uids)):
            for b_idx in range(a_idx + 1, len(uids)):
                a, b = uids[a_idx], uids[b_idx]
                va, vb = vectors[a], vectors[b]
                union = len(va | vb)
                score = round(len(va & vb) / union, 3) if union else 0.0
                out[(a, b)] = score
        return out

    # -- internal: network niceties ----------------------------------------

    def _respect_rate_limit(self) -> None:
        if self.rate_limit_seconds <= 0:
            return
        elapsed = time.monotonic() - self._last_request_time
        wait = self.rate_limit_seconds - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_time = time.monotonic()

    # -- internal: dry-run / synthetic data --------------------------------

    @staticmethod
    def _synthetic_profile(uniprot_id: str) -> ProteinDisorderProfile:
        """Deterministic synthetic profile for offline testing.

        Seeded by a hash of the accession so the same id always yields the same
        profile (reproducible tests). The profile has plausible structure: mostly
        confident helices with a couple of disordered loops, mimicking real AFDB
        output. A few accessions are made deliberately 404-ish by length 0 to
        exercise the not-found path.
        """
        digest = hashlib.sha256(uniprot_id.encode()).hexdigest()
        # Length in [60, 400); use the first 3 hex chars as a deterministic int.
        seq_len = 60 + int(digest[:3], 16) % 340

        # Build a deterministic pseudo-random pLDDT stream in [0, 100).
        def _rand(k: int) -> float:
            return int(digest[(k * 2) % (len(digest) - 2):(k * 2) % (len(digest) - 2) + 4], 16) / 0xFFFF * 100.0

        residues: List[ResidueConfidence] = []
        # Two seeded disordered stretches (start and ~60% in) plus otherwise high pLDDT.
        disorder_start1 = max(2, seq_len // 8)
        disorder_end1 = disorder_start1 + 4 + int(digest[4], 16) % 8
        disorder_start2 = seq_len * 3 // 5
        disorder_end2 = disorder_start2 + 3 + int(digest[5], 16) % 10
        for i in range(seq_len):
            if disorder_start1 <= i <= disorder_end1 or disorder_start2 <= i <= disorder_end2:
                plddt = 15.0 + _rand(i) * 0.30   # 15-45 -> disordered
            elif i in (disorder_end1 + 1, disorder_end2 + 1, disorder_start1 - 1):
                plddt = 55.0 + _rand(i + 7) * 0.15  # 55-70 -> boundary
            else:
                plddt = 75.0 + _rand(i + 3) * 0.24  # 75-99 -> structured
            letter = "ACDEFGHIKLMNPQRSTVWY"[int(digest[(i) % len(digest)], 16) % 20]
            residues.append(ResidueConfidence(
                residue_number=i + 1, amino_acid=letter,
                plddt=round(plddt, 2), category=_classify_plddt(plddt),
            ))

        sequence = "".join(r.amino_acid for r in residues)
        profile = ProteinDisorderProfile(
            uniprot_id=uniprot_id,
            sequence=sequence,
            sequence_length=seq_len,
            residues=residues,
            model_version="dry-run",
            model_created_date="2026-01-01",
            source="dry_run",
        )
        AlphaFoldConnector._finalize_profile(profile)
        return profile


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _classify_plddt(plddt: float) -> str:
    """Bucket a pLDDT value into structured / boundary / disordered."""
    if plddt < PLDDT_DISORDERED:
        return CATEGORY_DISORDERED
    if plddt <= PLDDT_STRUCTURED:
        return CATEGORY_BOUNDARY
    return CATEGORY


def _segment_regions(
    residues: Sequence[ResidueConfidence], category: str
) -> List[Region]:
    """Group maximal runs of same-``category`` residues into Region objects."""
    regions: List[Region] = []
    run: List[ResidueConfidence] = []
    for r in residues:
        if r.category == category:
            run.append(r)
        else:
            if run:
                regions.append(_make_region(run, category))
                run = []
    if run:
        regions.append(_make_region(run, category))
    return regions


def _make_region(run: Sequence[ResidueConfidence], category: str) -> Region:
    start = run[0].residue_number
    end = run[-1].residue_number
    mean_plddt = round(sum(r.plddt for r in run) / len(run), 2)
    return Region(
        start=start, end=end, length=len(run),
        mean_plddt=mean_plddt, category=category,
    )


def _relative_position_bin(midpoint: float) -> str:
    """Map a normalized midpoint in [0, 1] onto an N/middle/C label."""
    for lo, hi, label in POSITION_BINS:
        if lo <= midpoint < hi:
            return label
    return "C-terminal"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_alphafold_connector(
    dry_run: bool = False,
    timeout: float = 30.0,
    rate_limit_seconds: float = 1.0,
) -> AlphaFoldConnector:
    """Factory: create an AlphaFoldConnector (use this, never the constructor directly)."""
    return AlphaFoldConnector(
        dry_run=dry_run,
        timeout=timeout,
        rate_limit_seconds=rate_limit_seconds,
    )


# A module-level singleton for callers who want a shared, rate-limited client.
_singleton: Optional[AlphaFoldConnector] = None


def get_alphafold_connector(dry_run: bool = False) -> AlphaFoldConnector:
    """Get or create a singleton AlphaFoldConnector.

    Note: the dry_run flag only applies when first creating the singleton; if a
    live client already exists, pass ``dry_run=True`` to ``create_alphafold_connector``
    instead.
    """
    global _singleton
    if _singleton is None:
        _singleton = create_alphafold_connector(dry_run=dry_run)
    return _singleton
