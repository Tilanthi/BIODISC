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
"""P0.3 — Defect C: group labels must come from real sample metadata.

The downloaders fabricated case/control assignment (alternating), which makes
differential-expression results meaningless. These tests pin the corrected
behavior: groups are derived from !Sample_characteristics, or None (reject)
when undeterminable. Never fabricated.
"""
import numpy as np

from biodisc_core.fixed_pipeline.sample_metadata_parser import (
    parse_groups_from_series_matrix,
)

# Realistic GEO series-matrix header: one !Sample_characteristics_ch1 line per
# characteristic, values tab-separated and quoted across the 4 samples.
_T = "\t"
MATRIX = _T.join([
    "!Sample_geo_accession",
    '"GSM1"', '"GSM2"', '"GSM3"', '"GSM4"',
]) + "\n" + \
"!Sample_characteristics_ch1" + _T.join([""] + [
    '"treatment: control"', '"treatment: control"',
    '"treatment: drug_x"', '"treatment: drug_x"',
]) + "\n" + \
"!Sample_characteristics_ch1" + _T.join([""] + [
    '"cell line: A549"', '"cell line: A549"', '"cell line: A549"', '"cell line: A549"',
])


def test_parses_real_groups_from_characteristics():
    g = parse_groups_from_series_matrix(MATRIX, "effect of drug_x")
    assert g is not None
    # control (2) vs drug_x (2); control sorts before drug_x -> label 0
    assert list(g.labels) == [0, 0, 1, 1]
    assert g.field == "treatment"
    assert g.values_map[0] == "treatment: control"
    assert g.values_map[1] == "treatment: drug_x"


def test_returns_none_when_groups_undeterminable():
    # Only an accession line, no binary characteristic -> cannot determine groups
    ambiguous = "!Sample_geo_accession" + _T.join([""] + ['"GSM1"', '"GSM2"']) + "\n"
    assert parse_groups_from_series_matrix(ambiguous, "some question") is None


def test_returns_none_for_non_binary_characteristic():
    # A characteristic with 3 distinct values is not a usable binary grouping
    matrix = "!Sample_characteristics_ch1" + _T.join([""] + [
        '"stage: I"', '"stage: II"', '"stage: III"', '"stage: II"',
    ]) + "\n"
    assert parse_groups_from_series_matrix(matrix) is None


def test_handles_equals_separator_form():
    # Some GEO matrices use '!Field = v1\\tv2' instead of tab after the field name.
    matrix = (
        '!Sample_characteristics_ch1 = "treatment: control"\t"treatment: control"\t'
        '"treatment: drug"\t"treatment: drug"\n'
    )
    g = parse_groups_from_series_matrix(matrix)
    assert g is not None
    assert list(g.labels) == [0, 0, 1, 1]


def test_empty_input_returns_none():
    assert parse_groups_from_series_matrix("") is None
    assert parse_groups_from_series_matrix(None) is None  # type: ignore[arg-type]
