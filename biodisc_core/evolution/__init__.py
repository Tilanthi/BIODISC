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
"""AlphaEvolve-style evolutionary method discovery for BIODISC (Phase 1+).

Evolves the *code* of a bioinformatics method (here: a differential-expression
scoring function) via LLM-proposed search-and-replace diffs, scored by the
automated evaluator from biodisc_core.fixed_pipeline.benchmark.

This is CODE evolution (AlphaEvolve's mechanism), deliberately distinct from
the parameter/numeric evolution in biodisc_core.swarm.leapcore_evolution (which
mutates numeric Gene values and cannot represent open-ended program code).
"""
