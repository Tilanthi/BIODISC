"""b.2 — GPL probe->gene mapper (pure logic)."""
from biodisc_core.fixed_pipeline.probe_gene_mapping.gpl_mapper import (
    detect_probe_platform, extract_platform_id, _parse_gpl_table, map_probes,
)


GPL_SNIPPET = (
    "!platform_table_begin\n"
    "ID\tGene symbol\tGB_ACC\n"
    "1007_s_at\tDDR1\tU48805\n"
    "117_at\tHSPA6\tL27712\n"
    "1552286_s_at\tREPS2\tAL050050\n"
    "!platform_table_end\n"
)


def test_detect_probe_platform():
    assert detect_probe_platform(["ILMN_1343291", "ILMN_1343292"]) == "illumina"
    assert detect_probe_platform(["1007_s_at", "117_at"]) == "affy"
    assert detect_probe_platform(["TP53", "BRCA1", "EGFR"]) is None


def test_extract_platform_id():
    text = "!Series_platform_id = GPL570\n!Series_title = x\n"
    assert extract_platform_id(text) == "GPL570"
    assert extract_platform_id("no platform here") is None


def test_parse_gpl_table_maps_probes_to_symbols():
    m = _parse_gpl_table(GPL_SNIPPET)
    assert m["1007_s_at"] == "DDR1"
    assert m["117_at"] == "HSPA6"
    assert m["1552286_s_at"] == "REPS2"


def test_parse_gpl_table_refuses_without_gene_column():
    # ID + GB_ACC but no Gene symbol column -> refuse (return empty), never guess.
    bad = "!platform_table_begin\nID\tGB_ACC\n1007_s_at\tU48805\n!platform_table_end\n"
    assert _parse_gpl_table(bad) == {}


def test_parse_gpl_table_takes_first_of_multiple_symbols():
    snip = ("!platform_table_begin\nID\tGene symbol\n"
            "1007_s_at\tDDR1, MIR-1\n!platform_table_end\n")
    assert _parse_gpl_table(snip)["1007_s_at"] == "DDR1"


def test_map_probes_keeps_only_mapped():
    syms, kept = map_probes(
        ["1007_s_at", "117_at", "UNMAPPED_PROBE"],
        {"1007_s_at": "DDR1", "117_at": "HSPA6"},
    )
    assert syms == ["DDR1", "HSPA6"]
    assert kept == [0, 1]
