#!/usr/bin/env python3
"""Fix capabilities module imports to wrap all versioned imports in try/except"""

# This script wraps all versioned imports (V50, V60, V70, V95) in try/except blocks

import re

# Read the file
with open('/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/capabilities/__init__.py', 'r') as f:
    content = f.read()

# Define the version sections that need to be wrapped
# For now, let's just wrap the problematic imports individually

# Fix v70 imports - wrap each section individually
v70_imports = [
    ('v70_algorithmic_discovery', 'AlgorithmicDiscoveryEngine'),
    ('v70_universal_causal', 'UniversalCausalSubstrate'),
    ('v70_predictive_geometry', 'PredictiveInformationGeometry'),
    ('v70_meta_scientific', 'MetaScientificReasoner'),
    ('v70_emergent_computation', 'EmergentComputationLayer'),
    ('v70_temporal_hierarchy', 'TemporalHierarchyLearner'),
    ('v70_analogical_transfer', 'DeepAnalogicalTransferEngine'),
    ('v70_hypothesis_generator', 'HypothesisSpaceGenerator'),
    ('v70_synthetic_intelligence', 'V70SyntheticIntelligence'),
]

# Fix v95 imports
v95_imports = [
    ('v95_semantic_grounding', 'SemanticGroundingLayer'),
]

def wrap_import_section(content, module_name, class_name):
    """Wrap an import section in try/except"""
    # Find the import line
    pattern = rf'(from .{module_name} import \([^)]+\))'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"Could not find {module_name} import")
        return content

    import_block = match.group(1)

    # Check if it's already wrapped
    if 'try:' in content[max(0, match.start()-50):match.start()]:
        print(f"{module_name} already wrapped in try/except")
        return content

    # Create wrapped version
    wrapped_import = f"""try:
    {import_block}
    {class_name.upper()}_AVAILABLE = True
except ImportError:
    {class_name.upper()}_AVAILABLE = False
    logger.warning("{class_name} not available")"""

    # Replace the original import
    content = content[:match.start()] + wrapped_import + content[match.end():]

    return content

# Apply fixes to all problematic imports
for module_name, class_name in v70_imports + v95_imports:
    content = wrap_import_section(content, module_name, class_name)
    print(f"Fixed {module_name}")

# Write the fixed content back
with open('/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/capabilities/__init__.py', 'w') as f:
    f.write(content)

print("All capabilities imports fixed!")
