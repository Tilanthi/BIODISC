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
"""ConvergenceScorer (rebuild item 5) — multi-method agreement gating.

The science-of-science evidence (CD index, Uzzi atypical-combinations, paradigm-
overturn case studies) shows breakthrough signals are individually NOISY. The
case studies of real paradigm-overturns (endosymbiosis, prions, adult
neurogenesis) succeeded when MULTIPLE INDEPENDENT lines of evidence converged.
This scorer requires >= ``min_methods`` independent methods to agree on a
candidate before flagging it ``high_potential`` — cutting false positives from
any single noisy method.
"""
from __future__ import annotations

from typing import List

from .candidate import CandidatePool, DiscoveryCandidate


class ConvergenceScorer:
    """Score a CandidatePool: set convergence_score + high_potential on each candidate.

    convergence_score = number of distinct methods that flagged the candidate
    (after merging by convergence_key). high_potential = convergence_score >= min_methods.
    """

    def __init__(self, min_methods: int = 3):
        self.min_methods = min_methods

    def score_pool(self, pool: CandidatePool) -> List[DiscoveryCandidate]:
        for c in pool.all():
            c.convergence_score = len(set(c.methods))
            c.high_potential = c.convergence_score >= self.min_methods
        # rank: high_potential first, then by ev, then convergence_score
        ranked = sorted(pool.all(),
                        key=lambda c: (c.high_potential, c.ev, c.convergence_score),
                        reverse=True)
        return ranked

    def high_potential(self, pool: CandidatePool) -> List[DiscoveryCandidate]:
        return [c for c in self.score_pool(pool) if c.high_potential]
