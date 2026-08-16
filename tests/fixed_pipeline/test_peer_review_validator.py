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
"""Regression: peer-review logging must not crash on the reproducibility field.

_log_review_result referenced result.reproducibility_score, but the PeerReviewResult
dataclass field is `reproducibility` -> validate_discovery_for_peer_review always
crashed internally, so peer review never worked. This pins the fix.
"""
from biodisc_core.fixed_pipeline.peer_review_validator import (
    PeerReviewResult, PeerReviewDecision, create_peer_review_validator,
)


def test_log_review_result_does_not_crash():
    v = create_peer_review_validator()
    decision = next(iter(PeerReviewDecision))
    r = PeerReviewResult(
        decision=decision, novelty_score=8.0, scientific_merit=7.0,
        data_quality=7.0, reproducibility=6.0, overall_score=28.0,
        critical_issues=[], minor_issues=[], recommendations=[],
    )
    # Previously raised AttributeError: 'PeerReviewResult' has no attribute
    # 'reproducibility_score'.
    v._log_review_result(r)
    assert r.reproducibility == 6.0
    assert r.overall_score == 28.0
