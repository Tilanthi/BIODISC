#!/usr/bin/env python3
"""
Dataset Verification Script

This script VERIFIES that datasets actually exist in their repositories
before we claim they're "real" for use in BIODISC discoveries.

CRITICAL: Scientific integrity requires verification, not assumption.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from biodisc_core.fixed_pipeline.dataset_verifier_real import create_dataset_verifier
from biodisc_core.fixed_pipeline.real_datasets import (
    REAL_GEO_DATASETS,
    REAL_ARRAYEXPRESS_DATASETS,
    REAL_SRA_DATASETS,
    REAL_PRIDE_DATASETS
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def verify_datasets_from_list(dataset_list, repository_name: str, verifier):
    """Verify a list of datasets"""

    logger.info(f"\n{'=' * 80}")
    logger.info(f"VERIFYING {repository_name} DATASETS")
    logger.info(f"{'=' * 80}")

    verified = []
    failed = []

    for dataset in dataset_list:
        accession = dataset['id']
        logger.info(f"\nChecking {accession}...")

        if repository_name == 'GEO':
            exists, metadata = verifier.verify_geo_dataset(accession)
        elif repository_name == 'ARRAYEXPRESS':
            exists, metadata = verifier.verify_arrayexpress_dataset(accession)
        elif repository_name == 'SRA':
            exists, metadata = verifier.verify_sra_dataset(accession)
        elif repository_name == 'PRIDE':
            exists, metadata = verifier.verify_pride_dataset(accession)
        else:
            logger.warning(f"Unknown repository: {repository_name}")
            continue

        if exists:
            verified.append(dataset)
            logger.info(f"✅ {accession} VERIFIED - metadata received")
        else:
            failed.append(dataset)
            logger.error(f"❌ {accession} DOES NOT EXIST or is inaccessible")

    logger.info(f"\n{repository_name} Verification Results:")
    logger.info(f"  Total: {len(dataset_list)}")
    logger.info(f"  ✅ Verified: {len(verified)}")
    logger.info(f"  ❌ Failed: {len(failed)}")

    if failed:
        logger.warning(f"\n⚠️  FAILED DATASETS in {repository_name}:")
        for dataset in failed[:5]:  # Show first 5 failed
            logger.warning(f"   {dataset['id']} - {dataset.get('title', 'Unknown')}")

    return verified, failed


def main():
    """Verify all datasets across all repositories"""

    verifier = create_dataset_verifier()

    logger.info("=" * 80)
    logger.info("BIODISC DATASET VERIFICATION")
    logger.info("=" * 80)
    logger.info("\nVerifying that datasets actually exist BEFORE using them")
    logger.info("This prevents the pseudo-science problem of claiming datasets are 'real'")
    logger.info("when they don't actually exist.\n")

    # Verify GEO datasets
    geo_verified, geo_failed = verify_datasets_from_list(
        REAL_GEO_DATASETS[:5],  # Test first 5
        'GEO',
        verifier
    )

    # Verify ArrayExpress datasets
    ae_verified, ae_failed = verify_datasets_from_list(
        REAL_ARRAYEXPRESS_DATASETS[:3],  # Test first 3
        'ARRAYEXPRESS',
        verifier
    )

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 80)

    total_tested = len(REAL_GEO_DATASETS[:5]) + len(REAL_ARRAYEXPRESS_DATASETS[:3])
    total_verified = len(geo_verified) + len(ae_verified)
    total_failed = len(geo_failed) + len(ae_failed)

    logger.info(f"Total datasets tested: {total_tested}")
    logger.info(f"✅ Verified (actually exist): {total_verified}")
    logger.info(f"❌ Failed (don't exist): {total_failed}")

    if total_verified > 0:
        logger.info(f"\n✅ SUCCESS: We have {total_verified} VERIFIED datasets to use")
        logger.info("These datasets have been verified to actually exist in their repositories")
    else:
        logger.error(f"\n❌ PROBLEM: None of the datasets could be verified")
        logger.error("We need to either:")
        logger.error("1. Find datasets that actually exist")
        logger.error("2. Implement proper downloaders for repositories")
        logger.error("3. Start with a smaller number of verified datasets")

    logger.info("\n" + "=" * 80)
    logger.info("This verification prevents claiming datasets are 'real'")
    logger.info("when we haven't actually verified their existence.")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
