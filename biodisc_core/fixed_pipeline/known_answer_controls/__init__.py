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
"""Real-data known-answer control suite (V9.1) — the pipeline must recover what it verified.

Paper2Agent's reference-agreement testing, translated: run the method, pin what
it produced, and require agreement on every later run. BIODISC's analogue seeds
control cases from the GENUINE store (each finding = dataset + verified genes +
directions) and re-runs the real DE analyzer: the genes must come back
same-direction and significant. This is the daily tripwire for wiring bugs the
synthetic AUROC benchmark cannot see — the GPL probe->gene mapping bug and the
V8.0.34 orientation bug (a channel silently dead for 10 versions) would both
have been a failing control instead of forensics.

Statuses are labeled, never silently green:
``PASS | FAIL_DIRECTION | FAIL_SIGNIFICANCE | FAIL_ABSENT | SKIP_NO_DATA | ERROR``.

Run: ``python -m biodisc_core.fixed_pipeline.known_answer_controls --seed``
then ``python -m biodisc_core.fixed_pipeline.known_answer_controls [--max-cases N]``.
"""
from . import cases, runner  # noqa: F401

__all__ = ["cases", "runner"]
