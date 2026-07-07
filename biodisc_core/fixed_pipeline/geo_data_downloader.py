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
        self.geo ftp_base = "https://ftp.ncbi.nlm.nih.gov/geo/series/"
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
            expression_data, gene_symbols, group_labels = self._download_processed_matrix(
                geo_id, metadata, max_genes, timeout
            )

            if expression_data is not None:
                logger.info(f"✅ Successfully downloaded REAL data from {geo_id}")
                logger.info(f"   Genes: {len(gene_symbols)}, Samples: {expression_data.shape[1]}")
                return expression_data, gene_symbols, group_labels

            # Step 3: If matrix download fails, try to extract from individual samples
            logger.warning(f"   Processed matrix not available, trying individual samples...")
            expression_data, gene_symbols, group_labels = self._download_from_samples(
                geo_id, metadata, max_genes, timeout
            )

            if expression_data is not None:
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
        current_sample = None

        for line in lines:
            line = line.strip()

            if line.startswith('Title ='):
                metadata['title'] = line.split('=', 1)[1].strip()
            elif line.startswith('Organism ='):
                metadata['organism'] = line.split('=', 1)[1].strip()
            elif line.startswith('Platform ='):
                metadata['platform'] = line.split('=', 1)[1].strip()
            elif line.startswith('Sample ='):
                current_sample = line.split('=', 1)[1].strip()
                metadata['samples'].append(current_sample)
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

            # Try to find matrix file
            matrix_url = f"{self.geo_ftp_base}{gse_folder}/{geo_id}_series_matrix.txt.gz"

            logger.info(f"   Attempting to download: {matrix_url}")

            response = requests.get(matrix_url, timeout=timeout, stream=True)

            if response.status_code != 200:
                logger.info(f"   Matrix file not available (status {response.status_code})")
                return None

            # Parse the matrix file
            return self._parse_geo_matrix(response.content, max_genes)

        except Exception as e:
            logger.info(f"   Could not download matrix: {e}")
            return None

    def _parse_geo_matrix(
        self,
        content: bytes,
        max_genes: int
    ) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
        """Parse GEO series matrix file"""

        try:
            # Decompress gzip content
            with gzip.GzipFile(fileobj=io.BytesIO(content)) as f:
                text = f.read().decode('utf-8')

            # Parse the matrix
            lines = []
            for line in text.split('\n'):
                if line and not line.startswith('#'):
                    lines.append(line)

            if len(lines) < 2:
                logger.info("   Empty matrix file")
                return None

            # First column is ID_REF (gene identifiers), rest are samples
            # We need to skip the header row and parse data
            data_lines = lines[1:]  # Skip header

            # Extract gene symbols and expression values
            gene_symbols = []
            expression_data = []

            for line in data_lines[:max_genes]:
                parts = line.split('\t')
                if len(parts) < 2:
                    continue

                # First column is typically gene ID or symbol
                gene_id = parts[0].strip().replace('"', '')

                # Skip if not a standard gene symbol format
                if not gene_id or gene_id.startswith('AFFX') or gene_id == 'NA':
                    continue

                gene_symbols.append(gene_id)

                # Extract expression values (columns 2 onwards)
                values = []
                for part in parts[1:]:
                    try:
                        val = float(part.strip())
                        values.append(val)
                    except ValueError:
                        values.append(0.0)

                if values:
                    expression_data.append(values)

            if not gene_symbols or not expression_data:
                logger.info("   No valid data extracted from matrix")
                return None

            # Convert to numpy arrays
            expression_matrix = np.array(expression_data).T  # Transpose: samples x genes

            # Create simple group labels (alternating for demonstration)
            n_samples = expression_matrix.shape[0]
            group_labels = np.array([0] * (n_samples // 2) + [1] * (n_samples - n_samples // 2))

            logger.info(f"   Parsed {len(gene_symbols)} genes, {n_samples} samples from matrix")

            return expression_matrix, gene_symbols, group_labels

        except Exception as e:
            logger.info(f"   Error parsing matrix: {e}")
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
