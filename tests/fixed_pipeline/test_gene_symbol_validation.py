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
"""P0.1 — Defect A: probe IDs must NOT be accepted as valid gene symbols.

The HARD GATE (orchestrator step 2.5) previously accepted ILMN_######## and
numeric Affymetrix IDs as VALID gene symbols, so probe IDs leaked through into
published discoveries. These tests pin the corrected behavior.
"""
from biodisc_core.fixed_pipeline.gene_symbol_validation import (
    create_gene_symbol_validator,
)


def test_illumina_probe_id_is_rejected_as_gene_symbol():
    v = create_gene_symbol_validator()
    _, all_valid = v.validate_gene_symbols(
        gene_symbols=["ILMN_1659893", "TP53"], reject_on_invalid=True
    )
    assert all_valid is False, "ILMN_ probe IDs must NOT be accepted as valid gene symbols"


def test_numeric_affy_probe_id_is_rejected():
    v = create_gene_symbol_validator()
    _, all_valid = v.validate_gene_symbols(
        gene_symbols=["117_at", "BRCA1"], reject_on_invalid=True
    )
    assert all_valid is False


def test_control_probe_is_rejected():
    v = create_gene_symbol_validator()
    _, all_valid = v.validate_gene_symbols(
        gene_symbols=["AFFX-BioB-5_at", "EGFR"], reject_on_invalid=True
    )
    assert all_valid is False


def test_real_gene_symbols_still_pass():
    v = create_gene_symbol_validator()
    _, all_valid = v.validate_gene_symbols(
        gene_symbols=["TP53", "BRCA1", "EGFR", "GAPDH"], reject_on_invalid=True
    )
    assert all_valid is True


def test_ensembl_gene_id_still_valid():
    # ENSG IDs are real gene identifiers (not probes) and should remain valid.
    v = create_gene_symbol_validator()
    results = v.validate_gene_symbols(
        gene_symbols=["ENSG00000141510"], reject_on_invalid=False
    )
    validations = results[0]
    assert validations[0].result.value == "valid"
