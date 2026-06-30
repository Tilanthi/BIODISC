#!/usr/bin/env python3
"""
Reassess all autonomous discoveries using the V74 Genuine Discovery Filter.

This script loads the V74 filter directly (bypassing import issues) and
re-evaluates all discoveries to identify which are genuine vs data-gathering.
"""

import json
import sys
sys.path.insert(0, '/Users/gjw255/astrodata/SWARM/BIODISC')

import importlib.util

# Load V74 filter directly
spec = importlib.util.spec_from_file_location(
    'v74_filter',
    '/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/capabilities/v1xx_genuine_discovery_filter.py'
)
v74_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v74_module)

filter = v74_module.GenuineDiscoveryFilter()

# Load discoveries
with open('/Users/gjw255/astrodata/SWARM/BIODISC/autonomous_discoveries.jsonl', 'r') as f:
    discoveries = [json.loads(line) for line in f]

print("RE-EVALUATING ALL DISCOVERIES WITH V74 GENUINE DISCOVERY FILTER")
print("=" * 80)

genuine_discoveries = []
data_gathering_discoveries = []
trivial_discoveries = []

for discovery in discoveries:
    question = discovery.get('question', '')
    confidence = discovery.get('confidence', 0)
    discovery_id = discovery.get('id', '')

    # Assess with V74 filter
    assessment = filter.assess_question(question)

    result = {
        'id': discovery_id,
        'question': question,
        'confidence': confidence,
        'should_filter_out': assessment.should_filter_out,
        'is_genuine_contribution': assessment.is_genuine_contribution,
        'contribution_type': assessment.contribution_type.value if assessment.contribution_type else None
    }

    if assessment.should_filter_out:
        if assessment.is_genuine_contribution:
            genuine_discoveries.append(result)
        else:
            data_gathering_discoveries.append(result)
    else:
        # Should filter out means it's bad
        if 'What is' in question and len(question.split()) <= 4:
            trivial_discoveries.append(result)
        else:
            data_gathering_discoveries.append(result)

print(f"\n📊 SUMMARY:")
print(f"Total discoveries: {len(discoveries)}")
print(f"Genuine discoveries: {len(genuine_discoveries)}")
print(f"Data-gathering/summary: {len(data_gathering_discoveries)}")
print(f"Trivial definitions: {len(trivial_discoveries)}")

print(f"\n🔬 GENUINE DISCOVERIES ({len(genuine_discoveries)}):")
for i, d in enumerate(genuine_discoveries, 1):
    print(f"{i}. [{d['confidence']:.2f}] {d['question']}")

print(f"\n📚 DATA-GATHERING/-summary DISCOVERIES ({len(data_gathering_discoveries)}):")
for i, d in enumerate(data_gathering_discoveries[:10], 1):
    print(f"{i}. [{d['confidence']:.2f}] {d['question']}")
if len(data_gathering_discoveries) > 10:
    print(f"... and {len(data_gathering_discoveries) - 10} more")

print(f"\n❌ TRIVIAL DEFINITION DISCOVERIES ({len(trivial_discoveries)}):")
for i, d in enumerate(trivial_discoveries[:5], 1):
    print(f"{i}. {d['question']}")
if len(trivial_discoveries) > 5:
    print(f"... and {len(trivial_discoveries) - 5} more")

print(f"\n🎯 CORRECTED TOP 10 GENUINE DISCOVERIES:")
# Sort genuine discoveries by confidence
genuine_discoveries.sort(key=lambda x: x['confidence'], reverse=True)
for i, d in enumerate(genuine_discoveries[:10], 1):
    print(f"{i}. [{d['confidence']:.2f}] {d['question']}")