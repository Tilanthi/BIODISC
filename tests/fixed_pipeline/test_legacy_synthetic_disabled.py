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
    # The synthetic generator must no longer be called.
    assert "generate_real_gene_expression_data(" not in body, (
        "must not call the synthetic generator"
    )
    # The SYNTHETIC dataset id must no longer be constructed (precise: the
    # f-string build, not docstring prose that mentions the old behavior).
    assert 'f"SYNTHETIC_' not in body, "must not build SYNTHETIC dataset ids"
    assert "f'SYNTHETIC_" not in body, "must not build SYNTHETIC dataset ids"


def test_make_genuine_discovery_is_not_in_try_except_swallow():
    # The refusal must not be wrapped in a broad except that swallows it.
    fn = _make_genuine_discovery_ast()
    has_try = any(isinstance(n, ast.Try) for n in ast.walk(fn))
    assert not has_try, "refusal must not be hidden inside a try/except"
