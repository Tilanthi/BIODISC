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
"""Method-acquisition admission route (V9.1) — verified tool adoption, no invention.

Paper2Agent's rule — "Do not invent scientific algorithms to fill repository
gaps" — answers BIODISC's standing question of where new analysis capabilities
come from. Previously: the RSI miner / an LLM writes them (invention). Now:

* **admission** — a scientific method enters the pipeline only bound to
  peer-reviewed source (repo + commit + paper), quarantined until it carries
  evidence for reference agreement, a store false-positive check, and human
  review. Paper2Agent converted 74/100 papers even with heavy verification —
  acquired methods get their own quarantine, exactly like discovery candidates.
* **policy** — the RSI miner stays confined to PLUMBING (ontology maps, IO,
  reliability, orchestration). Scientific-algorithm proposals are routed to the
  acquisition queue instead of direct application.
"""
from . import admission, policy  # noqa: F401

__all__ = ["admission", "policy"]
