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
"""P0.4 + P0.5 — Defects D & E on the ACTIVE verifier.

The orchestrator uses multi_repository_verification.verify_dataset_comprehensive
(not the legacy dataset_verifier_real). That verifier (a) never parsed real
metadata (returned stub 'Dataset from <repo>', sample_count absent -> 0 in
records), and (b) accepted datasets regardless of sample count. These tests
pin real GEO metadata parsing + a minimum-sample-count gate.
"""
from unittest.mock import patch

from biodisc_core.fixed_pipeline.multi_repository_verification import (
    create_multi_repository_verifier,
)

GEO_SOFT = "\n".join([
    "!Series_title = Effect of drug_x on A549 cells",
    "!Series_organism = Homo sapiens",
    "!Series_sample_id = GSM1",
    "!Series_sample_id = GSM2",
    "!Series_sample_id = GSM3",
    "!Series_geo_accession = GSM4",
    "!Series_geo_accession = GSM5",
    "!Series_geo_accession = GSM6",
    "series_matrix_table_begin",
    '"ID_REF"\t"GSM1"\t"GSM2"',
    '"TP53"\t1.0\t2.0',
]) + "\n"


def test_parses_real_geo_metadata_from_response():
    v = create_multi_repository_verifier()
    from biodisc_core.fixed_pipeline.multi_repository_verification import (
        RepositoryConfig, RepositoryType,
    )
    cfg = RepositoryConfig(
        name="GEO", repository_type=RepositoryType.GEO,
        base_url="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi",
        accession_pattern=r"GSE\d+",
        data_types=["gene_expression"], description="GEO",
    )
    info = v._parse_repository_response(GEO_SOFT, cfg, "GSE12345")
    assert info["title"] == "Effect of drug_x on A549 cells"
    assert info["organism"] == "Homo sapiens"
    # 3 !Series_sample_id + 3 !Series_geo_accession = 6 samples
    assert info["sample_count"] == 6


def test_rejects_low_sample_count():
    v = create_multi_repository_verifier()
    with patch.object(
        v, "_verify_in_repository",
        return_value=(True, {"accession": "GSE1", "sample_count": 3}),
    ):
        success, info, msg = v.verify_dataset_comprehensive("GSE12345", "q")
    assert success is False
    assert "sample" in msg.lower()


def test_accepts_sufficient_sample_count():
    v = create_multi_repository_verifier()
    with patch.object(
        v, "_verify_in_repository",
        return_value=(True, {"accession": "GSE1", "sample_count": 10}),
    ):
        success, info, msg = v.verify_dataset_comprehensive("GSE12345", "q")
    assert success is True


def test_unknown_sample_count_does_not_hard_reject():
    # Repos where we cannot parse sample_count must not be hard-rejected on
    # sample-count grounds (would break non-GEO repos). Enforce where measurable.
    v = create_multi_repository_verifier()
    with patch.object(
        v, "_verify_in_repository",
        return_value=(True, {"accession": "PXD000001", "sample_count": None}),
    ):
        success, info, msg = v.verify_dataset_comprehensive("PXD000001", "q")
    assert success is True
