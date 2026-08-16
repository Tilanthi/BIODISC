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
"""Test probe ID to gene symbol mapping."""
import pytest
from biodisc_core.fixed_pipeline.probe_gene_mapping import (
    create_probe_gene_mapper,
    GeneResolutionResult,
    PlatformParser
)

def test_detect_probe_ids():
    """Test detection of probe IDs vs gene symbols."""
    parser = PlatformParser()

    # Pure numeric - probe IDs
    probes = ['455', '1195', '382', '551', '1739']
    has_probes, fraction = parser.detect_probe_ids(probes)
    assert has_probes
    assert fraction == 1.0

    # Gene symbols
    genes = ['BRCA1', 'TP53', 'EGFR', 'MYC']
    has_probes, fraction = parser.detect_probe_ids(genes)
    assert not has_probes
    assert fraction == 0.0

    # Mixed (>50% probes to trigger detection)
    mixed = ['BRCA1', '455', '1195', '382', 'TP53']
    has_probes, fraction = parser.detect_probe_ids(mixed)
    assert has_probes  # >50% probe threshold
    assert fraction == 0.6  # 3/5 are probes

def test_gene_symbols_passthrough():
    """Test that gene symbols pass through without resolution."""
    mapper = create_probe_gene_mapper()

    identifiers = ['BRCA1', 'TP53', 'EGFR', 'MYC']
    result = mapper.validate_and_resolve(identifiers)

    assert result.success
    assert result.resolved_genes == identifiers
    assert len(result.unmapped_probes) == 0
    assert result.mapping_rate == 1.0

def test_probe_id_rejection():
    """Test that probe IDs are rejected (critical test for peer review fix)."""
    mapper = create_probe_gene_mapper()

    # These are the exact probe IDs from the peer review case
    probes = ['455', '1195', '382', '551', '1739']
    result = mapper.validate_and_resolve(probes)

    # Should FAIL - cannot use probe IDs as genes
    assert not result.success
    assert len(result.unmapped_probes) == 5
    assert result.warning_message is not None
    assert 'probe' in result.warning_message.lower()

def test_mixed_identifiers():
    """Test handling of mixed probe IDs and gene symbols."""
    mapper = create_probe_gene_mapper()

    mixed = ['BRCA1', '455', '1195', '382', 'TP53']
    result = mapper.validate_and_resolve(mixed)

    # Should FAIL due to unmapped probes
    assert not result.success
    assert '455' in result.unmapped_probes
    assert '1195' in result.unmapped_probes
    assert 'BRCA1' in result.resolved_genes

def test_affymetrix_probe_format():
    """Test detection of Affymetrix probe ID format."""
    parser = PlatformParser()

    # Affymetrix format: 12345_at
    affy_probes = ['1007_s_at', '1053_at', '117_at']
    has_probes, _ = parser.detect_probe_ids(affy_probes)
    assert has_probes

    # Gene symbols
    genes = ['BRCA1', 'TP53']
    has_probes, _ = parser.detect_probe_ids(genes)
    assert not has_probes

def test_illumina_probe_format():
    """Test detection of Illumina probe ID format."""
    parser = PlatformParser()

    # Illumina format: ILMN_12345
    illumina_probes = ['ILMN_12345', 'ILMN_67890']
    has_probes, _ = parser.detect_probe_ids(illumina_probes)
    assert has_probes

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
