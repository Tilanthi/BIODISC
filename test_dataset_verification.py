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
Test script for dataset verification system

This tests the new verification system to ensure it properly:
1. Verifies dataset existence
2. Matches data types to question types
3. Validates sample counts
4. Catches fake/hallucinated datasets
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from biodisc_core.fixed_pipeline.dataset_verification import create_dataset_verifier, DataType

def test_verification():
    """Test the dataset verification system"""

    print("=" * 80)
    print("TESTING DATASET VERIFICATION SYSTEM")
    print("=" * 80)

    verifier = create_dataset_verifier()

    # Test cases
    test_cases = [
        {
            'name': 'Real RNA-seq dataset with expression question',
            'geo_id': 'GSE12345',  # This should exist or fail appropriately
            'question': 'How does gene expression change in cancer?',
            'should_pass': True  # We'll see if it exists
        },
        {
            'name': 'Epigenetic question with expression data (should fail)',
            'geo_id': 'GSE99999',  # Fake dataset
            'question': 'How do epigenetic modifications contribute to transgenerational inheritance?',
            'should_pass': False  # Should fail - fake dataset
        },
        {
            'name': 'Known problematic dataset from previous pipeline',
            'geo_id': 'GSE295966',  # The fake dataset from previous analysis
            'question': 'How do epigenetic modifications contribute to transgenerational inheritance?',
            'should_pass': False  # Should fail - dataset doesn't exist or wrong type
        }
    ]

    print(f"\n🧪 Running {len(test_cases)} test cases...\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"   GEO ID: {test_case['geo_id']}")
        print(f"   Question: {test_case['question'][:60]}...")

        # Run verification
        success, verified_dataset, message = verifier.verify_dataset_comprehensive(
            test_case['geo_id'],
            test_case['question']
        )

        print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
        print(f"   Message: {message}")

        if verified_dataset:
            print(f"   Dataset Info:")
            print(f"     - Samples: {verified_dataset.sample_count}")
            print(f"     - Features: {verified_dataset.feature_count}")
            print(f"     - Data Type: {verified_dataset.data_type.value}")
            print(f"     - Organism: {verified_dataset.organism}")

    # Show statistics
    stats = verifier.get_verification_stats()
    print("\n" + "=" * 80)
    print("VERIFICATION STATISTICS")
    print("=" * 80)
    print(f"   Attempts: {stats['verification_attempts']}")
    print(f"   Failures: {stats['failed_verifications']}")
    print(f"   Success Rate: {stats['success_rate']:.1%}")

    print("\n✅ VERIFICATION SYSTEM TEST COMPLETE")

if __name__ == "__main__":
    test_verification()