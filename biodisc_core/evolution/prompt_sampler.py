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
"""Prompt sampler for the evolutionary loop (AlphaEvolve).

Assembles a rich evolution prompt: the parent program + its evaluation results,
diverse high-performing inspirations from the archive, the scoring contract, and
a stochastic "style" hint for candidate diversity. Deterministic given the rng.
"""
import random
from typing import List, Optional, Tuple

from .meta_prompt import MetaPrompt
from .program_db import ArchivedProgram


SYSTEM_PROMPT = """\
You are an evolutionary coding agent improving a bioinformatics method.
The task: improve the `score(expression, labels)` function so it better
identifies truly differentially-expressed genes.

CONTRACT (a valid program MUST satisfy all of these):
- define `def score(expression, labels)`
- expression: np.ndarray shape (n_genes, n_samples); labels: np.ndarray of {0,1}
- return a 1D np.ndarray shape (n_genes,); HIGHER value = more differentially expressed
- you may `import numpy as np` and `from scipy import stats` inside the function

FITNESS (what you are optimizing):
- aggregate = 0.6 * AUROC + 0.4 * held_out_replicate
- AUROC: how well your per-gene scores rank truly-DE genes above others
- held_out_replicate: the SAME method on an independent dataset — rewards
  generalization, NOT overfitting. Do not hard-code to the data.

OUTPUT FORMAT — return ONLY search-and-replace diffs, nothing else:
<<< SEARCH
exact lines from the current program to replace (must match verbatim)
===
the replacement lines
>>> REPLACE

You may emit multiple blocks. For a full rewrite, emit the entire new `def score`
function with no markers. Do not add commentary or markdown fences.
"""

STYLE_HINTS = [
    "Make a minimal, surgical change.",
    "Try a more robust statistic (e.g. Welch's t, rank-based, moderated).",
    "Improve numerical stability / handle edge cases.",
    "Try a different normalization or variance estimate.",
    "Combine two signals (e.g. effect size and significance).",
    "Rethink the scoring approach more boldly, using an inspiration.",
]


def build_evolution_prompt(
    parent: ArchivedProgram,
    inspirations: List[ArchivedProgram],
    generation: int,
    rng: random.Random,
    meta_prompt: Optional[MetaPrompt] = None,
) -> Tuple[str, str]:
    """Return (system, user) prompt for one evolution step."""
    style = rng.choice(STYLE_HINTS)

    lines = []
    lines.append(f"=== GENERATION {generation} ===")
    lines.append(f"Goal: improve aggregate fitness (currently {parent.aggregate:.3f}, "
                 f"AUROC {parent.auroc:.3f}, held-out replicate {parent.replicate_concordance:.3f}).")
    lines.append(f"Style hint for diversity: {style}")
    if meta_prompt is not None:
        lines.append(f"Co-evolved strategy guidance: {meta_prompt.text}")
    lines.append("")
    lines.append("=== CURRENT PROGRAM (parent) ===")
    lines.append(parent.source.strip("\n"))

    if inspirations:
        lines.append("")
        lines.append("=== INSPIRATIONS (other archived programs; borrow ideas, do not copy blindly) ===")
        for i, ins in enumerate(inspirations):
            lines.append(f"--- inspiration {i + 1} (aggregate {ins.aggregate:.3f}) ---")
            lines.append(ins.source.strip("\n"))

    lines.append("")
    lines.append("Emit your improvement as diff blocks now.")
    user = "\n".join(lines)
    return SYSTEM_PROMPT, user
