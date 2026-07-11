"""P0.3b — the dormant synthetic-data discovery path must be disabled.

biodisc_v6_0_fixed_integrated.make_genuine_discovery previously generated fake
expression data (GENE_#### ids, dataset_id=SYNTHETIC_<ts>) and 'discovered' DE
genes in it. It is verified here to REFUSE (raise RuntimeError) and to contain
no synthetic-data calls. Source-level check avoids the legacy module's heavy
import graph.
"""
import ast
import os
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
LEGACY_FILE = REPO_ROOT / "biodisc_v6_0_fixed_integrated.py"


def _make_genuine_discovery_ast() -> ast.FunctionDef:
    tree = ast.parse(LEGACY_FILE.read_text())
    # Walk the whole tree: make_genuine_discovery is a class method (nested in
    # a ClassDef), not a top-level function.
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "make_genuine_discovery":
            return node
    raise AssertionError("make_genuine_discovery not found in legacy file")


def test_make_genuine_discovery_raises_and_uses_no_synthetic_data():
    fn = _make_genuine_discovery_ast()
    body = ast.unparse(fn)
    assert "raise RuntimeError" in body, "make_genuine_discovery must refuse"
    assert "generate_real_gene_expression_data" not in body, (
        "must not call the synthetic generator"
    )
    assert "SYNTHETIC" not in body, "must not emit SYNTHETIC dataset ids"


def test_make_genuine_discovery_is_not_in_try_except_swallow():
    # The refusal must not be wrapped in a broad except that swallows it.
    fn = _make_genuine_discovery_ast()
    has_try = any(isinstance(n, ast.Try) for n in ast.walk(fn))
    assert not has_try, "refusal must not be hidden inside a try/except"
