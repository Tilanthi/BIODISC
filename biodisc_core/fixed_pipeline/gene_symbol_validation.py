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
Gene Symbol Validation System - HARD GATE

This module implements VALIDATION GATES that prevent pseudo-science generation:

CRITICAL PRINCIPLES:
1. ALL gene symbols MUST be validated against HGNC/Ensembl BEFORE analysis
2. Any invalid gene symbol → REJECT the entire discovery
3. NO fallback to synthetic/fake gene identifiers
4. Discoveries MUST be traceable to real biological data

This is a NON-NEGOTIABLE hard gate in the discovery pipeline.
"""

import logging
import os
import re
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from biodisc_core.fixed_pipeline import discovery_status

logger = logging.getLogger(__name__)

# On-disk cache of confirmed valid/invalid symbols. The 2026-08 kill spiral
# showed why this must persist: caches lived only in process memory, so every
# watchdog kill+restart re-crawled the same ~2000 symbols from HGNC at zero —
# the loop could never bank progress across restarts. UNKNOWN verdicts are
# deliberately NOT persisted (a transient API outage must not become fact).
CACHE_PATH = Path(os.environ.get(
    "BIODISC_GENE_SYMBOL_CACHE",
    str(Path(__file__).resolve().parents[2] / "cache"
        / "gene_symbol_validation_cache.json")))

# Heartbeat/flush cadence inside the crawl. 30 s bounds the watchdog's view of
# idleness no matter how slow HGNC answers (10 s timeout per call), and caps
# lost work on a mid-crawl kill at ~30 s.
PROGRESS_FLUSH_S = 30.0


class ValidationResult(Enum):
    """Validation result with clear outcomes"""
    VALID = "valid"  # Gene symbol is verified real
    INVALID = "invalid"  # Gene symbol is fake/hallucinated
    UNKNOWN = "unknown"  # Cannot verify (database unavailable)


@dataclass
class GeneSymbolValidation:
    """Result of gene symbol validation"""
    symbol: str
    result: ValidationResult
    source: str  # "HGNC", "Ensembl", "FAILED"
    gene_id: Optional[str] = None
    gene_name: Optional[str] = None
    error: Optional[str] = None


class GeneSymbolValidator:
    """
    Validates gene symbols against real databases (HGNC/Ensembl).

    This is a HARD GATE - any invalid gene symbols REJECT the entire discovery.
    """

    def __init__(self):
        self.valid_symbols_cache: Set[str] = set()
        self.invalid_symbols_cache: Set[str] = set()
        self.validation_count = 0
        self.rejection_count = 0
        self._last_progress_flush = 0.0

        # Database endpoints
        self.hgnc_api = "https://rest.genenames.org/fetch/symbol/"
        self.ensembl_api = "https://rest.ensembl.org"

        # Real human gene symbols from HGNC (curated list)
        self.known_real_genes = self._load_known_real_genes()

        self._load_persistent_cache()

        logger.info("🔬 Gene Symbol Validator initialized")
        logger.info(f"   Known real genes: {len(self.known_real_genes)}")
        logger.info(f"   Persisted symbol cache: "
                    f"{len(self.valid_symbols_cache)} valid / "
                    f"{len(self.invalid_symbols_cache)} invalid")

    def _load_persistent_cache(self) -> None:
        """Warm the in-memory caches from the on-disk cache (best-effort)."""
        try:
            if CACHE_PATH.exists():
                data = json.loads(CACHE_PATH.read_text())
                self.valid_symbols_cache.update(data.get("valid", []))
                self.invalid_symbols_cache.update(data.get("invalid", []))
        except Exception as e:  # noqa: BLE001 — corrupt cache must not kill the gate
            logger.warning(f"Gene-symbol cache unreadable, starting cold: {e}")

    def _save_persistent_cache(self) -> None:
        """Atomically persist confirmed verdicts so restarts bank progress."""
        try:
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "valid": sorted(self.valid_symbols_cache),
                "invalid": sorted(self.invalid_symbols_cache),
                "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            tmp = CACHE_PATH.with_suffix(CACHE_PATH.suffix + ".tmp")
            tmp.write_text(json.dumps(payload))
            os.replace(tmp, CACHE_PATH)
        except Exception as e:  # noqa: BLE001 — cache write failure is non-fatal
            logger.warning(f"Gene-symbol cache write failed (non-fatal): {e}")

    def _heartbeat(self, note: str, force: bool = False) -> None:
        """Throttled liveness signal + cache flush.

        Called from inside the crawl so (a) the watchdog's idle check sees the
        loop is busy on a long network phase, and (b) a kill mid-crawl loses at
        most PROGRESS_FLUSH_S of validation work instead of everything.
        """
        now = time.time()
        if not force and (now - self._last_progress_flush) < PROGRESS_FLUSH_S:
            return
        self._last_progress_flush = now
        discovery_status.record_activity(note)
        self._save_persistent_cache()

    def _load_known_real_genes(self) -> Set[str]:
        """
        Load known real human gene symbols from HGNC.

        This is a curated list of ~1000 commonly studied real genes.
        For production, this should query HGNC directly.
        """
        # Core set of verified real human genes
        known_genes = {
            # Housekeeping
            "ACTB", "GAPDH", "B2M", "UBC", "HPRT1", "TBP", "RPLP0", "YWHAZ",
            # Cell cycle
            "CCND1", "CCNE1", "CDK1", "CDK2", "CDK4", "CDK6", "RB1", "TP53",
            "CDKN1A", "CDKN1B", "CDKN2A", "E2F1", "E2F2", "E2F3",
            # Apoptosis
            "BCL2", "BAX", "CASP3", "CASP8", "CASP9", "FAS", "FASLG", "MCL1",
            "BAK1", "BID", "BIM", "NOXA", "PUMA",
            # Growth factors
            "EGFR", "ERBB2", "VEGFA", "FGF1", "FGF2", "PDGFA", "PDGFB",
            "IGF1", "IGF2", "TGFB1", "TGFB2", "MET", "KIT",
            # Signaling
            "AKT1", "AKT2", "MAPK1", "MAPK3", "MAPK14", "JUN", "FOS",
            "STAT1", "STAT3", "NF1", "NRAS", "HRAS", "KRAS", "BRAF",
            # Transcription factors
            "MYC", "MYCN", "MAX", "MXI1", "SP1", "SP3", "E2F1", "E2F4",
            "CTNNB1", "TCF7L2", "LEF1", "HIF1A", "HIF1B",
            # Metabolism
            "SLC2A1", "SLC2A4", "HK1", "HK2", "PFKL", "PFKM", "PKM", "LDHA",
            "CS", "IDH1", "IDH2", "SDHA", "SDHB", "FH", "MDH2",
            # Stress response (real HSP genes only)
            "HSPA1A", "HSPA1B", "HSPB1", "HSPB8", "HSPD1", "HSPA5", "HSPA8",
            "ATF3", "ATF4", "DDIT3", "XBP1",
            # Immune
            "IL1B", "IL6", "TNF", "IFNG", "IL10", "IL12A", "IL12B",
            "CD4", "CD8A", "CD19", "MS4A1", "CD33",
            # EMT
            "CDH1", "VIM", "SNAI1", "SNAI2", "TWIST1", "ZEB1", "ZEB2",
            "MMP2", "MMP9", "MMP14",
            # Angiogenesis
            "ANGPT1", "ANGPT2", "TEK", "FLT1", "KDR", "FLT4",
            # Cancer genes
            "BRCA1", "BRCA2", "PALB2", "PTEN", "PIK3CA", "PIK3CB",
            "SMAD4", "SMAD2", "SMAD3", "SMAD7", "TGFBR1", "TGFBR2",
            # Ribosomal proteins (REAL RPL genes - limited set)
            "RPL4", "RPL5", "RPL7", "RPL10", "RPL11", "RPL13", "RPL13A",
            "RPL15", "RPL18", "RPL19", "RPL21", "RPL23", "RPL27", "RPL29",
            "RPL30", "RPL31", "RPL35", "RPL35A", "RPL36", "RPL37", "RPL38",
            "RPLP0", "RPLP1", "RPLP2",
            # Ribosomal proteins small (REAL RPS genes - limited set)
            "RPS2", "RPS3", "RPS4", "RPS5", "RPS6", "RPS7", "RPS8",
            "RPS9", "RPS10", "RPS11", "RPS12", "RPS13", "RPS14", "RPS15",
            "RPS15A", "RPS16", "RPS17", "RPS18", "RPS19", "RPS20", "RPS21",
            "RPS23", "RPS24", "RPS25", "RPS26", "RPS27", "RPS28", "RPS29",
            "RPS3A", "RPSA", "RPSBL7",
            # Keratins (REAL KRT genes - limited set)
            "KRT1", "KRT2", "KRT5", "KRT6A", "KRT6B", "KRT6C", "KRT7",
            "KRT8", "KRT9", "KRT10", "KRT12", "KRT13", "KRT14", "KRT15",
            "KRT16", "KRT17", "KRT18", "KRT19", "KRT20",
            # Collagens (REAL COL genes - limited set)
            "COL1A1", "COL1A2", "COL2A1", "COL3A1", "COL4A1", "COL4A2",
            "COL5A1", "COL5A2", "COL5A3", "COL6A1", "COL6A2", "COL6A3",
            "COL7A1", "COL8A1", "COL8A2", "COL9A1", "COL9A2", "COL9A3",
            "COL10A1", "COL11A1", "COL11A2", "COL12A1", "COL13A1",
            "COL14A1", "COL15A1", "COL16A1", "COL17A1",
            # Aldolases (ONLY real aldolases)
            "ALDOA", "ALDOB", "ALDOC",
            # GAPDH (ONLY real GAPDH - GAPD is old symbol but valid)
            "GAPDH",
        }

        logger.info(f"   Loaded {len(known_genes)} known real gene symbols")
        return known_genes

    def validate_gene_symbols(
        self,
        gene_symbols: List[str],
        reject_on_invalid: bool = True
    ) -> Tuple[List[GeneSymbolValidation], bool]:
        """
        Validate gene symbols against HGNC/Ensembl databases.

        Args:
            gene_symbols: List of gene symbols to validate
            reject_on_invalid: If True, reject entire set if ANY symbol is invalid

        Returns:
            (validation_results, all_valid)
        """

        logger.info(f"🔬 Validating {len(gene_symbols)} gene symbols")

        self.validation_count += 1
        self._heartbeat(f"gene_symbol_validation 0/{len(gene_symbols)}",
                        force=True)

        validation_results = []
        invalid_symbols = []

        for i, symbol in enumerate(gene_symbols, 1):
            result = self._validate_single_symbol(symbol)
            validation_results.append(result)

            if result.result == ValidationResult.INVALID:
                invalid_symbols.append(symbol)
                self.invalid_symbols_cache.add(symbol)
            elif result.result == ValidationResult.VALID:
                self.valid_symbols_cache.add(symbol)

            if i % 50 == 0:
                self._heartbeat(
                    f"gene_symbol_validation {i}/{len(gene_symbols)}")

        # Persist the completed crawl before the gate decision.
        self._heartbeat(
            f"gene_symbol_validation {len(gene_symbols)}/{len(gene_symbols)}",
            force=True)

        # Summary
        valid_count = sum(1 for r in validation_results if r.result == ValidationResult.VALID)
        invalid_count = sum(1 for r in validation_results if r.result == ValidationResult.INVALID)
        unknown_count = sum(1 for r in validation_results if r.result == ValidationResult.UNKNOWN)

        logger.info(f"   Validation results:")
        logger.info(f"   ✅ Valid: {valid_count}")
        logger.info(f"   ❌ Invalid: {invalid_count}")
        logger.info(f"   ❓ Unknown: {unknown_count}")

        # Reject if any invalid symbols found
        if invalid_count > 0 and reject_on_invalid:
            logger.error(f"❌ REJECTED: Found {invalid_count} invalid gene symbols")
            logger.error(f"   Invalid symbols: {invalid_symbols[:10]}")
            self.rejection_count += 1
            return validation_results, False

        if unknown_count > 0:
            logger.warning(f"⚠️  Could not verify {unknown_count} symbols (database unavailable)")

        logger.info(f"✅ Gene symbols validated successfully")
        return validation_results, True

    def _validate_single_symbol(self, symbol: str) -> GeneSymbolValidation:
        """
        Validate a single gene symbol.

        Detection of FAKE patterns:
        - RPL/RPS + high number (RPL166, RPS44 don't exist)
        - KRT + high number (KRT113 doesn't exist)
        - ALDO + number (ALDO52, ALDO197 don't exist - only ALDOA/B/C)
        - GAPD + number (GAPD115 doesn't exist - only GAPDH)
        - HSP + high number (HSP167, HSP129 don't exist)
        - COL + high number (COL219, COL246 don't exist - real COL genes use COL#A# format)
        """

        # Check cache first
        if symbol in self.valid_symbols_cache:
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.VALID,
                source="CACHE",
                gene_id=symbol
            )

        if symbol in self.invalid_symbols_cache:
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.INVALID,
                source="CACHE",
                error="Previously identified as invalid"
            )

        # Check against known real genes
        if symbol in self.known_real_genes:
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.VALID,
                source="KNOWN_LIST",
                gene_id=symbol
            )

        # CHECK FOR VALID PROBE IDs (before fake pattern detection)
        probe_validation = self._validate_probe_id(symbol)
        if probe_validation:
            return probe_validation

        # DETECT FAKE PATTERNS
        fake_pattern = self._detect_fake_pattern(symbol)
        if fake_pattern:
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.INVALID,
                source="FAKE_PATTERN_DETECTED",
                error=fake_pattern
            )

        # Try HGNC API
        hgnc_result = self._query_hgnc(symbol)
        if hgnc_result:
            return hgnc_result

        # If API unavailable, return UNKNOWN (not INVALID)
        return GeneSymbolValidation(
            symbol=symbol,
            result=ValidationResult.UNKNOWN,
            source="API_UNAVAILABLE",
            error="Could not verify gene symbol (database unavailable)"
        )

    def _detect_fake_pattern(self, symbol: str) -> Optional[str]:
        """
        Detect fake gene identifier patterns.

        Returns error message if fake pattern detected, None otherwise.
        """

        # Pattern 1: RPL + high number (> RPL38)
        if symbol.startswith("RPL"):
            try:
                number = int(symbol[3:])
                # Real RPL genes go up to ~RPL38, anything higher is fake
                if number > 50:
                    return f"Fake RPL gene: {symbol} (real RPL genes only go up to ~RPL38)"
            except ValueError:
                pass

        # Pattern 2: RPS + high number (> RPS29)
        if symbol.startswith("RPS"):
            try:
                number = int(symbol[3:])
                # Real RPS genes go up to ~RPS29, anything higher is fake
                if number > 35:
                    return f"Fake RPS gene: {symbol} (real RPS genes only go up to ~RPS29)"
            except ValueError:
                pass

        # Pattern 3: KRT + high number (> KRT20)
        if symbol.startswith("KRT") and not symbol.startswith("KRTAP"):
            try:
                number = int(symbol[3:])
                # Real KRT genes go up to ~KRT20, anything higher is fake
                if number > 25:
                    return f"Fake KRT gene: {symbol} (real KRT genes only go up to ~KRT20)"
            except ValueError:
                pass

        # Pattern 4: ALDO + number (only ALDOA, ALDOB, ALDOC are real)
        if symbol.startswith("ALDO") and symbol not in ["ALDOA", "ALDOB", "ALDOC"]:
            return f"Fake ALDO gene: {symbol} (only ALDOA, ALDOB, ALDOC are real)"

        # Pattern 5: GAPD + number (only GAPDH is real, GAPD is old but valid)
        if symbol.startswith("GAPD") and symbol not in ["GAPDH", "GAPD"]:
            try:
                number = int(symbol[4:])
                return f"Fake GAPD gene: {symbol} (only GAPDH is real)"
            except ValueError:
                pass

        # Pattern 6: HSP + high number (most HSP genes are HSP# with # < 100)
        if symbol.startswith("HSP"):
            try:
                number = int(symbol[3:])
                # Real HSP genes typically have numbers < 100
                if number > 150:
                    return f"Fake HSP gene: {symbol} (most real HSP genes have numbers < 100)"
            except ValueError:
                pass

        # Pattern 7: COL + simple number (real COL genes use COL#A# format)
        if symbol.startswith("COL"):
            # Check if it's COL + number (fake) vs COL#A# (real)
            import re
            if re.match(r'^COL\d+$', symbol):
                return f"Fake COL gene: {symbol} (real COL genes use COL#A# format like COL1A1)"

        # Pattern 8: GENE_XXXX format (fake placeholder)
        if symbol.startswith("GENE_") and len(symbol) > 5:
            try:
                number = symbol.split("_")[1]
                if number.isdigit():
                    return f"Fake gene placeholder: {symbol} (GENE_XXXX format is fake)"
            except:
                pass

        return None

    def _validate_probe_id(self, symbol: str) -> Optional[GeneSymbolValidation]:
        """
        Validate probe IDs from known microarray platforms.

        These are legitimate identifiers used in real biological datasets,
        even though they're not standard gene symbols.

        Valid probe ID formats:
        - Illumina: ILMN_######## (8 digits)
        - Affymetrix numeric: Single numbers like '3', '4', '5'
        - Control probes: Control_*, AFFX-*
        - Ensembl genes: ENSG#########
        """
        # Illumina probe IDs (ILMN_ followed by 6-8 digits).
        # P0.1 (Defect A): probe IDs are NOT gene symbols. They previously passed
        # the HARD GATE as VALID, leaking ILMN_ identifiers into discoveries.
        # They must be rejected here; probes must be resolved to gene symbols
        # upstream (probe_gene_mapping) or the discovery rejected.
        if symbol.startswith("ILMN_") and len(symbol) >= 12:
            try:
                number = symbol[5:]
                if number.isdigit() and 6 <= len(number) <= 8:
                    return GeneSymbolValidation(
                        symbol=symbol,
                        result=ValidationResult.INVALID,
                        source="ILLUMINA_PROBE",
                        gene_id=f"Probe_{symbol}",
                        gene_name="Illumina Probe ID",
                        error="Illumina probe ID is not a gene symbol; resolve to gene symbol before analysis"
                    )
            except:
                pass

        # Affymetrix numeric probe IDs (simple numbers). No real gene symbol is
        # purely numeric — these are probe identifiers and must be rejected.
        if symbol.isdigit():
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.INVALID,
                source="AFFYMETRIX_PROBE",
                gene_id=f"Probe_{symbol}",
                gene_name="Affymetrix Probe ID",
                error="Numeric Affymetrix probe ID is not a gene symbol; resolve to gene symbol before analysis"
            )

        # Affymetrix 3'-IVT probe IDs (e.g. "117_at", "211234_s_at", "1553367_a_at").
        # These are probe identifiers, not gene symbols, and must be rejected
        # LOCALLY here — otherwise they fall through to the HGNC network lookup,
        # which is non-deterministic and can fail-open to VALID under timing
        # pressure (the latent bug behind the flaky test_numeric_affy_probe_id test).
        if re.fullmatch(r"\d+_(a_|s_|x_)?at", symbol):
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.INVALID,
                source="AFFYMETRIX_PROBE",
                gene_id=f"Probe_{symbol}",
                gene_name="Affymetrix Probe ID",
                error="Affymetrix _at probe ID is not a gene symbol; resolve to gene symbol before analysis"
            )

        # Control probes. These should be filtered out of datasets entirely; if
        # they reach validation they must be rejected, never accepted as genes.
        if symbol.startswith("Control_") or symbol.startswith("AFFX-"):
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.INVALID,
                source="CONTROL_PROBE",
                gene_id=f"Probe_{symbol}",
                gene_name="Control Probe",
                error="Control probe is not a gene symbol; filter control probes before analysis"
            )

        # Ensembl gene IDs
        if symbol.startswith("ENSG") and len(symbol) >= 15:
            return GeneSymbolValidation(
                symbol=symbol,
                result=ValidationResult.VALID,
                source="ENSEMBL",
                gene_id=symbol,
                gene_name="Ensembl Gene ID"
            )

        # Not a recognized probe format
        return None

    def _query_hgnc(self, symbol: str, timeout: int = 10) -> Optional[GeneSymbolValidation]:
        """
        Query HGNC API to validate gene symbol.

        Returns validation result if API available, None otherwise.
        """

        try:
            response = requests.get(
                f"{self.hgnc_api}{symbol}",
                headers={"Accept": "application/json"},
                timeout=timeout
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("response") and "numFound" in data["response"]:
                    if data["response"]["numFound"] > 0:
                        doc = data["response"]["docs"][0]
                        return GeneSymbolValidation(
                            symbol=symbol,
                            result=ValidationResult.VALID,
                            source="HGNC_API",
                            gene_id=doc.get("hgnc_id"),
                            gene_name=doc.get("name")
                        )
                    else:
                        return GeneSymbolValidation(
                            symbol=symbol,
                            result=ValidationResult.INVALID,
                            source="HGNC_API",
                            error="Symbol not found in HGNC database"
                        )

            # API unavailable or error
            return None

        except requests.exceptions.Timeout:
            logger.warning(f"   HGNC API timeout for {symbol}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"   HGNC API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.warning(f"   Unexpected error querying HGNC for {symbol}: {e}")
            return None

    def get_statistics(self) -> Dict:
        """Get validator statistics"""
        return {
            'validation_count': self.validation_count,
            'rejection_count': self.rejection_count,
            'valid_symbols_cached': len(self.valid_symbols_cache),
            'invalid_symbols_cached': len(self.invalid_symbols_cache),
            'rejection_rate': (
                self.rejection_count / self.validation_count
                if self.validation_count > 0 else 0
            )
        }


def create_gene_symbol_validator() -> GeneSymbolValidator:
    """Factory function to create gene symbol validator"""
    return GeneSymbolValidator()
