"""
Real GEO Data Downloader

This module downloads ACTUAL gene expression data from NCBI GEO database.
This replaces synthetic/fake data generation with real biological data.

IMPORTANT: This is a critical component for scientific integrity.
"""

import requests
import logging
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional, Dict
import time
import gzip
import io

logger = logging.getLogger(__name__)


class GEODataDownloader:
    """
    Downloads real gene expression data from GEO database.

    This replaces synthetic data generation with actual biological data.
    """

    def __init__(self):
        self.geo_base_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
        self.geo_ftp_base = "https://ftp.ncbi.nlm.nih.gov/geo/series/"
        self.cache = {}

    def download_geo_dataset(
        self,
        geo_id: str,
        max_genes: int = 2000,
        timeout: int = 60
    ) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
        """
        Download real gene expression data from GEO dataset.

        Args:
            geo_id: GEO accession (e.g., GSE12345)
            max_genes: Maximum number of genes to extract
            timeout: Request timeout in seconds

        Returns:
            (expression_data, gene_symbols, group_labels) or None if download fails
        """

        logger.info(f"🌐 Attempting to download REAL GEO data for {geo_id}")

        try:
            # Step 1: Get dataset metadata
            metadata = self._get_geo_metadata(geo_id, timeout)
            if not metadata:
                logger.error(f"❌ Could not get metadata for {geo_id}")
                return None

            logger.info(f"✅ Metadata retrieved for {geo_id}")
            logger.info(f"   Title: {metadata.get('title', 'N/A')}")
            logger.info(f"   Organism: {metadata.get('organism', 'N/A')}")
            logger.info(f"   Samples: {metadata.get('sample_count', 0)}")

            # Step 2: Try to download processed matrix file
            matrix_result = self._download_processed_matrix(
                geo_id, metadata, max_genes, timeout
            )

            if matrix_result is not None:
                expression_data, gene_symbols, group_labels = matrix_result
                logger.info(f"✅ Successfully downloaded REAL data from {geo_id}")
                logger.info(f"   Genes: {len(gene_symbols)}, Samples: {expression_data.shape[1]}")
                return expression_data, gene_symbols, group_labels

            # Step 3: If matrix download fails, try to extract from individual samples
            logger.warning(f"   Processed matrix not available, trying individual samples...")
            sample_result = self._download_from_samples(
                geo_id, metadata, max_genes, timeout
            )

            if sample_result is not None:
                expression_data, gene_symbols, group_labels = sample_result
                logger.info(f"✅ Successfully extracted data from {geo_id} samples")
                return expression_data, gene_symbols, group_labels

            logger.error(f"❌ Could not extract data from {geo_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Error downloading {geo_id}: {e}")
            return None

    def _get_geo_metadata(self, geo_id: str, timeout: int) -> Optional[Dict]:
        """Get GEO dataset metadata"""

        try:
            params = {
                'acc': geo_id,
                'targ': 'summary',
                'view': 'full',
                'form': 'text'
            }

            response = requests.get(
                self.geo_base_url,
                params=params,
                timeout=timeout
            )

            if response.status_code != 200:
                logger.warning(f"   Status {response.status_code} from GEO")
                return None

            # Parse metadata from response
            metadata = self._parse_geo_metadata(response.text, geo_id)
            return metadata

        except Exception as e:
            logger.error(f"   Error getting metadata: {e}")
            return None

    def _parse_geo_metadata(self, text: str, geo_id: str) -> Dict:
        """Parse GEO metadata from text response"""

        metadata = {
            'geo_id': geo_id,
            'title': '',
            'organism': '',
            'sample_count': 0,
            'platform': '',
            'samples': []
        }

        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # GEO uses !Series_ prefix for metadata
            if line.startswith('!Series_title ='):
                metadata['title'] = line.split('=', 1)[1].strip()
            elif line.startswith('!Series_organism ='):
                metadata['organism'] = line.split('=', 1)[1].strip()
            elif line.startswith('!Series_platform ='):
                metadata['platform'] = line.split('=', 1)[1].strip()
            elif line.startswith('!Series_sample_id ='):
                sample_id = line.split('=', 1)[1].strip()
                metadata['samples'].append(sample_id)
                metadata['sample_count'] += 1

        return metadata

    def _download_processed_matrix(
        self,
        geo_id: str,
        metadata: Dict,
        max_genes: int,
        timeout: int
    ) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
        """Download processed matrix file from GEO"""

        try:
            # Convert GSE### to GSE###nnn format for FTP
            gse_num = geo_id.replace('GSE', '')
            gse_folder = f"GSE{gse_num[:-3]}nnn/{geo_id}/matrix"

            # Try multiple possible matrix file naming patterns
            possible_patterns = [
                f"{geo_id}_series_matrix.txt.gz",  # Standard pattern
                f"{geo_id}-*_series_matrix.txt.gz",   # Platform-specific pattern
            ]

            # First try to list the matrix directory to see what files exist
            matrix_dir_url = f"{self.geo_ftp_base}{gse_folder}/"

            logger.info(f"   Checking matrix directory: {matrix_dir_url}")

            try:
                response = requests.get(matrix_dir_url, timeout=timeout)
                if response.status_code == 200:
                    # Parse HTML to find matrix files
                    import re
                    matrix_files = re.findall(r'href="([^"]*_series_matrix\.txt\.gz)"', response.text)

                    if matrix_files:
                        # Use the first matrix file found
                        matrix_filename = matrix_files[0]
                        matrix_url = f"{self.geo_ftp_base}{gse_folder}/{matrix_filename}"
                        logger.info(f"   Found matrix file: {matrix_filename}")
                    else:
                        logger.info(f"   No matrix files found in directory")
                        return None
                else:
                    logger.info(f"   Matrix directory not accessible (status {response.status_code})")
                    return None
            except Exception as e:
                logger.info(f"   Could not list matrix directory: {e}")
                return None

            logger.info(f"   Attempting to download: {matrix_url}")

            # The matrix file can be very large (hundreds of MB; ~2 GB for big
            # studies like GSE13159 with 2096 samples). The shared `timeout`
            # (default 60 s) is fine for the tiny metadata / directory-listing
            # calls, but it fires intermittently between byte chunks on a large
            # streamed download, causing spurious "Cannot download real data"
            # failures that waste discovery cycles. Use a dedicated (connect,
            # read) timeout with a generous read window for the matrix only, and
            # retry once on transient resets. Connect still fails fast (15 s).
            MATRIX_TIMEOUT = (15, 180)
            response = None
            for attempt in range(2):
                try:
                    response = requests.get(matrix_url, timeout=MATRIX_TIMEOUT, stream=True)
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == 0:
                        logger.info(f"   Matrix download transient error, retrying: {e}")
                        time.sleep(3)
                    else:
                        logger.info(f"   Matrix download failed after retry: {e}")
                        return None

            if response is None or response.status_code != 200:
                logger.info(f"   Matrix file not available (status {getattr(response, 'status_code', None)})")
                return None

            # Read the streamed body with a hard TOTAL deadline + size cap. A
            # plain ``response.content`` read can hang indefinitely on a stalled
            # mid-stream connection (the per-chunk read timeout does not always
            # fire on half-open sockets) — this is what stalled the discovery
            # loop for hours. Bounding total wall-clock + bytes guarantees the
            # call always returns.
            content = self._read_stream_bounded(
                response, max_seconds=600, max_bytes=600 * 1024 * 1024)
            if content is None:
                return None
            return self._parse_geo_matrix(content, max_genes)

        except Exception as e:
            logger.info(f"   Could not download matrix: {e}")
            return None

    def _read_stream_bounded(
        self,
        response,
        max_seconds: int = 600,
        max_bytes: int = 600 * 1024 * 1024,
    ) -> Optional[bytes]:
        """Read a streamed response with a hard total-time and total-size bound."""
        start = time.monotonic()
        chunks = []
        total = 0
        try:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    logger.warning(
                        f"   Matrix exceeds {max_bytes // (1024 * 1024)} MB cap, aborting download")
                    return None
                if time.monotonic() - start > max_seconds:
                    logger.warning(
                        f"   Matrix download exceeded {max_seconds}s deadline, aborting")
                    return None
                chunks.append(chunk)
            logger.info(f"   Streamed {total // (1024 * 1024)} MB in "
                        f"{time.monotonic() - start:.0f}s")
            return b"".join(chunks)
        except requests.exceptions.RequestException as e:
            logger.info(f"   Matrix stream read failed: {e}")
            return None

    def _parse_geo_matrix(
        self,
        content: bytes,
        max_genes: int
    ) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
        """Parse GEO series matrix file with robust error handling"""

        try:
            # Decompress gzip content
            with gzip.GzipFile(fileobj=io.BytesIO(content)) as f:
                text = f.read().decode('utf-8', errors='ignore')

            logger.info(f"   Decompressed {len(text)} characters")

            # Find the data section (starts with "ID_REF" header)
            lines = text.split('\n')

            data_start_line = -1
            for i, line in enumerate(lines):
                if 'ID_REF' in line or '"ID_REF"' in line:
                    data_start_line = i
                    break

            if data_start_line == -1:
                logger.info("   Could not find data section (ID_REF header)")
                return None

            logger.info(f"   Found data section at line {data_start_line}")

            # Parse data starting from the line after ID_REF
            data_lines = lines[data_start_line + 1:]

            gene_symbols = []
            expression_data = []
            max_cols = 0

            # Extract data rows
            for line in data_lines[:max_genes]:
                line = line.strip()
                if not line:
                    continue

                # Split by tab, keeping empty strings
                parts = line.split('\t')

                if len(parts) < 2:
                    continue

                # First column is ID_REF (gene identifier or symbol)
                gene_id = parts[0].strip().replace('"', '').replace("'", '')

                # Skip empty or invalid identifiers
                if not gene_id or gene_id in ['NA', 'null', '']:
                    continue

                # Skip ALL control probe patterns (not just AFFX-)
                # Common control probe prefixes:
                # - AFFX-: Affymetrix control probes
                # - Control_: Generic control probes
                # - CONTROL_: Uppercase variant
                # - Blank_: Background/blank controls
                # - BLANK_: Uppercase background controls
                # - BioB_: Spike-in controls
                # - BioC_: Spike-in controls
                # - BioD_: Spike-in controls
                # - A_: Some platforms use A_ for controls
                # - Orf _: ORF control probes
                # - Neg _: Negative controls
                control_prefixes = [
                    'AFFX-', 'Control_', 'CONTROL_', 'Blank_', 'BLANK_',
                    'BioB_', 'BioC_', 'BioD_', 'A_', 'Orf_', 'Neg_',
                    'PseudoAffx_', 'Spike_', 'ERCC_', 'External_'
                ]

                is_control_probe = any(gene_id.startswith(prefix) for prefix in control_prefixes)

                if is_control_probe:
                    logger.debug(f"   Skipping control probe: {gene_id}")
                    continue

                gene_symbols.append(gene_id)

                # Extract expression values (columns 1 onwards, skipping ID_REF)
                values = []
                for part in parts[1:]:  # Skip first column (ID_REF)
                    part = part.strip()
                    if not part or part in ['null', 'NA', '']:
                        values.append(0.0)
                    else:
                        try:
                            val = float(part)
                            values.append(val)
                        except ValueError:
                            # Try to handle "n/a", "inf", etc.
                            if part.lower() in ['n/a', 'null', 'na']:
                                values.append(0.0)
                            else:
                                values.append(0.0)

                if values:
                    expression_data.append(values)
                    max_cols = max(max_cols, len(values))

            if not gene_symbols:
                logger.info("   No valid gene symbols extracted")
                return None

            if not expression_data:
                logger.info("   No expression data extracted")
                return None

            # GPL probe -> gene-symbol mapping (real-data unlock). If the row IDs
            # are Affymetrix/Illumina probes, map them to gene symbols via the
            # platform GPL annotation so the downstream gene-symbol gate sees real
            # symbols. SAFE FALLBACK: on any failure or poor mapping rate, return
            # None (reject) rather than risk mis-mapping probes to wrong symbols.
            from biodisc_core.fixed_pipeline.probe_gene_mapping.gpl_mapper import (
                detect_probe_platform, extract_platform_id, load_gpl_symbol_map,
                map_probes, MIN_MAPPING_RATE,
            )
            if detect_probe_platform(gene_symbols):
                platform_id = extract_platform_id(text)
                mapping = load_gpl_symbol_map(platform_id) if platform_id else {}
                if not mapping:
                    logger.info(f"   REJECTING: probe-based rows with no GPL mapping "
                                f"(platform={platform_id}); refusing to publish probe IDs")
                    return None
                symbols, kept = map_probes(gene_symbols, mapping)
                rate = len(symbols) / max(1, len(gene_symbols))
                if rate < MIN_MAPPING_RATE:
                    logger.info(f"   REJECTING: GPL mapping rate {rate:.2f} < {MIN_MAPPING_RATE}")
                    return None
                logger.info(f"   GPL mapped {len(symbols)}/{len(gene_symbols)} probes -> "
                            f"gene symbols (rate {rate:.2f})")
                gene_symbols = symbols
                expression_data = [expression_data[i] for i in kept]

            # Pad all rows to have the same length
            padded_data = []
            for row in expression_data:
                if len(row) < max_cols:
                    padded_row = row + [0.0] * (max_cols - len(row))
                    padded_data.append(padded_row)
                else:
                    padded_data.append(row)

            # Convert to numpy arrays
            expression_matrix = np.array(padded_data, dtype=float)

            # Keep as genes x samples format (no transpose)
            # This matches what differential expression analyzer expects
            if expression_matrix.ndim == 1:
                expression_matrix = expression_matrix.reshape(-1, 1)

            # DO NOT transpose - keep as genes x samples
            # expression_matrix = expression_matrix.T  # Removed transpose

            n_genes_parsed, n_samples = expression_matrix.shape

            logger.info(f"   Parsed {n_genes_parsed} genes, {n_samples} samples from matrix")
            logger.info(f"   First 3 genes: {gene_symbols[:3]}")
            logger.info(f"   Matrix shape: {expression_matrix.shape} (genes x samples)")

            # P0.3 (Defect C): derive REAL group labels from !Sample_* metadata.
            # Never fabricate the case/control split — a fabricated split makes
            # all differential-expression results statistical noise. Reject the
            # dataset if the experimental design cannot be recovered.
            from biodisc_core.fixed_pipeline.sample_metadata_parser import (
                parse_groups_from_series_matrix,
            )
            assignment = parse_groups_from_series_matrix(text)
            if assignment is None or len(assignment.labels) != n_samples:
                logger.warning(
                    f"   REJECTING dataset: cannot determine real group labels "
                    f"from sample metadata; refusing to fabricate case/control split"
                )
                return None
            group_labels = assignment.labels

            return expression_matrix, gene_symbols, group_labels

        except Exception as e:
            logger.info(f"   Error parsing matrix: {e}")
            import traceback
            logger.info(f"   Traceback: {traceback.format_exc()}")
            return None

    def _download_from_samples(
        self,
        geo_id: str,
        metadata: Dict,
        max_genes: int,
        timeout: int
    ) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
        """Download and parse data from individual samples"""

        # This is a more complex implementation that would download individual samples
        # For now, return None to indicate this method is not yet implemented
        logger.info("   Individual sample download not yet implemented")
        return None


def create_geo_data_downloader() -> GEODataDownloader:
    """Factory function to create GEO data downloader"""
    return GEODataDownloader()
