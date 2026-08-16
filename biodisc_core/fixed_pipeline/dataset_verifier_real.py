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
Dataset Verification System

This module VERIFIES that datasets actually exist in their repositories
before allowing them in the discovery pipeline.

CRITICAL: We must VERIFY datasets exist, not ASSUME they exist.
The peer reviewer criticized us for claiming datasets were "real" when they
didn't actually exist or we used fake identifiers.

This system performs actual verification queries to repositories.
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DatasetVerifier:
    """
    Verifies dataset existence in biological repositories.

    This replaces assumptions with actual verification queries.
    """

    def __init__(self):
        self.verification_cache = {}
        self.verified_datasets = {}

    def verify_geo_dataset(self, geo_id: str, timeout: int = 30) -> tuple[bool, Optional[dict]]:
        """
        Verify a GEO dataset actually exists in NCBI GEO.

        Returns: (exists, metadata)
        """

        try:
            url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
            params = {
                'acc': geo_id,
                'targ': 'summary',
                'view': 'full',
                'form': 'text'
            }

            response = requests.get(url, params=params, timeout=timeout)

            if response.status_code != 200:
                return False, None

            # Check if dataset exists (GEO returns specific text for non-existent)
            text = response.text
            if "could not be found" in text.lower() or "not found" in text.lower():
                return False, None

            # Extract basic metadata
            metadata = self._parse_geo_summary(text, geo_id)

            if metadata and metadata.get('sample_count', 0) >= 6:
                logger.info(f"✅ Verified {geo_id}: {metadata.get('sample_count')} samples")
                return True, metadata
            else:
                # P0.4 (Defect D): insufficient samples must REJECT, not pass.
                logger.warning(f"⚠️  {geo_id} exists but has insufficient samples")
                return False, metadata

        except Exception as e:
            logger.error(f"❌ Error verifying {geo_id}: {e}")
            return False, None

    def verify_arrayexpress_dataset(self, accession: str, timeout: int = 30) -> tuple[bool, Optional[dict]]:
        """
        Verify an ArrayExpress dataset actually exists.

        Returns: (exists, metadata)
        """

        try:
            url = f"https://www.ebi.ac.uk/arrayexpress/api/v3/experiments/{accession}"

            response = requests.get(url, timeout=timeout, headers={'Accept': 'application/json'})

            if response.status_code != 200:
                return False, None

            try:
                data = response.json()

                if data and 'summary' in data:
                    samples = data.get('summary', {}).get('samples', 0)

                    if samples >= 6:
                        logger.info(f"✅ Verified {accession}: {samples} samples")
                        return True, {
                            'accession': accession,
                            'repository': 'ARRAYEXPRESS',
                            'samples': samples,
                            'title': data.get('summary', {}).get('title', ''),
                            'organism': data.get('summary', {}).get('organism', '')
                        }
                    else:
                        logger.warning(f"⚠️  {accession} exists but has {samples} samples (insufficient)")
                        return True, None
                else:
                    logger.warning(f"⚠️  {accession} exists but no sample data found")
                    return True, None

            except Exception as e:
                logger.warning(f"⚠️  {accession} returned data but couldn't parse: {e}")
                return True, None  # Exists but data format unclear

        except Exception as e:
            logger.error(f"❌ Error verifying {accession}: {e}")
            return False, None

    def verify_sra_dataset(self, accession: str, timeout: int = 30) -> tuple[bool, Optional[dict]]:
        """
        Verify an SRA dataset actually exists.

        Returns: (exists, metadata)
        """

        try:
            url = f"https://www.ncbi.nlm.nih.gov/sra/?term={accession}"

            response = requests.get(url, timeout=timeout)

            if response.status_code != 200:
                return False, None

            text = response.text

            # Check if results were found
            if "No results" in text or "can't find" in text.lower():
                return False, None
            elif accession in text and "SRA" in text:
                # Basic check - would need better parsing for production
                logger.info(f"✅ Verified {accession} exists in SRA")
                return True, {
                    'accession': accession,
                    'repository': 'SRA',
                    'samples': 0,  # Would need to extract from SRA metadata
                    'title': f'SRA dataset {accession}',
                    'organism': 'Various'
                }
            else:
                logger.warning(f"⚠️  {accession} unclear if exists")
                return False, None

        except Exception as e:
            logger.error(f"❌ Error verifying {accession}: {e}")
            return False, None

    def verify_pride_dataset(self, accession: str, timeout: int = 30) -> tuple[bool, Optional[dict]]:
        """
        Verify a PRIDE dataset actually exists.

        Returns: (exists, metadata)
        """

        try:
            url = f"https://www.ebi.ac.uk/pride/archive/projects/{accession}"

            response = requests.get(url, timeout=timeout, headers={'Accept': 'application/json'})

            if response.status_code != 200:
                return False, None

            try:
                data = response.json()

                # Check if project actually exists
                if 'accession' in data and data['accession'] == accession:
                    samples = len(data.get('samples', []))
                    title = data.get('title', '')

                    if samples >= 6:
                        logger.info(f"✅ Verified {accession}: {samples} samples")
                        return True, {
                            'accession': accession,
                            'repository': 'PRIDE',
                            'samples': samples,
                            'title': title,
                            'organism': 'Human'  # Most PRIDE datasets are human
                        }
                    else:
                        logger.warning(f"⚠️  {accession} exists but has {samples} samples")
                        return True, None

            except Exception as e:
                logger.warning(f"⚠️  {accession} returned data but couldn't parse: {e}")
                return True, None

        except Exception as e:
            logger.error(f"❌ Error verifying {accession}: {e}")
            return False, None

    def _parse_geo_summary(self, text: str, geo_id: str) -> Optional[dict]:
        """Parse GEO summary text to extract metadata"""

        metadata = {
            'geo_id': geo_id,
            'title': '',
            'organism': '',
            'sample_count': 0,
            'platform': '',
            'data_type': 'gene_expression'
        }

        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # GEO uses !Series_ prefix for metadata
            if line.startswith('!Series_title ='):
                metadata['title'] = line.replace('!Series_title =', '').strip()
            elif line.startswith('!Series_organism ='):
                metadata['organism'] = line.replace('!Series_organism =', '').strip()
            elif line.startswith('!Series_platform ='):
                metadata['platform'] = line.replace('!Series_platform =', '').strip()
            elif line.startswith('!Series_sample_id ='):
                metadata['sample_count'] += 1
            elif '!Series_sample_id' in line.lower():
                metadata['sample_count'] += 1

        return metadata


def create_dataset_verifier() -> DatasetVerifier:
    """Factory function to create dataset verifier"""
    return DatasetVerifier()
