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
"""Breakthrough discovery package — the multi-modality rebuild.

The old pipeline was single-modality (one question -> one dataset -> DE). This
package implements the evidence-based rebuild: multiple independent discovery
*modalities* (cross-domain bridges, literature-claim contradictions, anomalies-in-
context, dataset re-mining) each emit ``DiscoveryCandidate`` objects into a shared
``CandidatePool``; a ``ConvergenceScorer`` (item 5) flags candidates that >=3
independent methods agree on as high-potential; the survivors flow through the
existing 6-layer validation + replication anchor (item 6) as the final gate.

Grounded in the multi-agent analysis of how real biology breakthroughs happen:
the highest-yield, automatable mechanisms are cross-domain synthesis, second-wave
data re-mining, and literature-vs-data contradiction — not single-contrast DE on
exhausted datasets.
"""
from .candidate import DiscoveryCandidate, CandidatePool
from .convergence import ConvergenceScorer

__all__ = ["DiscoveryCandidate", "CandidatePool", "ConvergenceScorer"]
