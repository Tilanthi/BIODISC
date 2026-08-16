#!/usr/bin/env python3
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
Test script to verify control probe filtering fix in GEO data downloader.
"""

import logging
import sys
from biodisc_core.fixed_pipeline.geo_data_downloader import create_geo_data_downloader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_control_probe_filtering():
    """Test that control probes are properly filtered out."""

    logger.info("🧪 Testing control probe filtering fix...")
    logger.info("=" * 60)

    # Test with a verified GEO dataset
    test_geo_id = "GSE11223"  # From real_datasets.py - tested working

    logger.info(f"📊 Testing with dataset: {test_geo_id}")

    # Create downloader and fetch data
    downloader = create_geo_data_downloader()
    result = downloader.download_geo_dataset(test_geo_id, max_genes=100)

    if result is None:
        logger.error("❌ Failed to download data")
        return False

    expression_data, gene_symbols, group_labels = result

    logger.info(f"✅ Successfully downloaded data")
    logger.info(f"   Total genes found: {len(gene_symbols)}")
    logger.info(f"   Expression matrix shape: {expression_data.shape}")
    logger.info(f"   Sample groups: {len(set(group_labels))} groups")

    # Check for control probes in the results
    logger.info("\n🔍 Checking for control probes in results...")

    control_prefixes = [
        'AFFX-', 'Control_', 'CONTROL_', 'Blank_', 'BLANK_',
        'BioB_', 'BioC_', 'BioD_', 'A_', 'Orf_', 'Neg_',
        'PseudoAffx_', 'Spike_', 'ERCC_', 'External_'
    ]

    control_probes_found = []
    real_genes = []

    for gene in gene_symbols:
        is_control = any(gene.startswith(prefix) for prefix in control_prefixes)
        if is_control:
            control_probes_found.append(gene)
        else:
            real_genes.append(gene)

    logger.info(f"   Control probes found: {len(control_probes_found)}")
    logger.info(f"   Real genes found: {len(real_genes)}")

    if control_probes_found:
        logger.error("❌ FAIL: Control probes found in results:")
        for probe in control_probes_found[:10]:  # Show first 10
            logger.error(f"   - {probe}")
        if len(control_probes_found) > 10:
            logger.error(f"   ... and {len(control_probes_found) - 10} more")
        return False
    else:
        logger.info("✅ PASS: No control probes found in results")

    # Show sample of real genes found
    logger.info(f"\n📊 Sample of real genes found (first 10):")
    for gene in real_genes[:10]:
        logger.info(f"   - {gene}")

    # Verify we have reasonable number of genes
    if len(real_genes) < 50:
        logger.warning(f"⚠️  Low gene count ({len(real_genes)}) - may indicate filtering is too strict")
    elif len(real_genes) > 0:
        logger.info("✅ PASS: Reasonable number of real genes found")

    logger.info("\n" + "=" * 60)
    logger.info("✅ Control probe filtering test PASSED")
    logger.info(f"   Filtering is working correctly - {len(real_genes)} real genes, 0 control probes")

    return True

if __name__ == "__main__":
    success = test_control_probe_filtering()
    sys.exit(0 if success else 1)
