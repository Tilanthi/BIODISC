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
"""P0.2 — Defect B: the probe resolver must not fabricate gene names.

resolve_probes_to_genes previously emitted f"UNKNOWN_GENE_{probe_id}" for
unmapped probes — a fabricated identifier worse than the probe itself. It must
emit None for unmapped probes and report success=False so the gate rejects.
"""
from biodisc_core.fixed_pipeline.probe_gene_mapping import create_probe_gene_mapper


def test_resolver_never_emits_unknown_gene_names():
    mapper = create_probe_gene_mapper()
    result = mapper.validate_and_resolve(["ILMN_1659893", "ILMN_0000000"])
    assert "UNKNOWN_GENE_ILMN_1659893" not in result.resolved_genes
    assert not any(
        isinstance(g, str) and g.startswith("UNKNOWN_GENE_")
        for g in result.resolved_genes
    ), f"Fabricated names found: {result.resolved_genes}"


def test_resolver_marks_unmapped_and_rejects():
    mapper = create_probe_gene_mapper()
    result = mapper.validate_and_resolve(["ILMN_1659893"])
    assert result.success is False
    assert "ILMN_1659893" in result.unmapped_probes


def test_real_symbols_pass_through():
    mapper = create_probe_gene_mapper()
    result = mapper.validate_and_resolve(["TP53", "BRCA1"])
    assert result.success is True
    assert result.resolved_genes == ["TP53", "BRCA1"]
