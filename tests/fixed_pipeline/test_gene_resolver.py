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
