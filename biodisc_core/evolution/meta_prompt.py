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
"""Co-evolved meta-prompts (AlphaEvolve §2.1).

AlphaEvolve co-evolves prompt INSTRUCTIONS in a separate database alongside
solution programs. Here a MetaPromptArchive holds short strategy directives;
each step the controller samples one, the LLM sees it, and on accept the
resulting program's fitness is credited back to that meta-prompt. Selection
(epsilon-greedy over empirical mean aggregate) then favors directives that
empirically produce better programs — closing the co-evolution loop without a
separate LLM call per directive.
"""
import random
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_META_PROMPTS: List[str] = [
    "Prefer robust, non-parametric statistics that resist outliers and unequal variance.",
    "Minimize code complexity: prefer vectorized numpy over Python loops.",
    "Combine effect size with significance into a single score.",
    "Try a variance-stabilizing or rank-based transform of the expression values.",
    "Improve numerical stability and handle edge cases (NaN, tiny groups).",
    "Reconsider the core scoring idea more boldly, drawing on an inspiration.",
]


@dataclass
class MetaPrompt:
    text: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    total: float = 0.0
    n_uses: int = 0

    @property
    def mean_aggregate(self) -> float:
        return self.total / self.n_uses if self.n_uses else 0.0

    def update(self, aggregate: float) -> None:
        self.total += aggregate
        self.n_uses += 1


class MetaPromptArchive:
    """Co-evolved pool of strategy directives, selected by empirical success."""

    def __init__(
        self,
        prompts: Optional[List[str]] = None,
        rng: Optional[random.Random] = None,
        epsilon: float = 0.2,
    ):
        texts = list(prompts) if prompts is not None else list(DEFAULT_META_PROMPTS)
        self.prompts: Dict[str, MetaPrompt] = {mp.id: mp for mp in (MetaPrompt(text=t) for t in texts)}
        self.rng = rng or random.Random(0)
        self.epsilon = epsilon
        self.last_id: Optional[str] = None

    def sample(self) -> MetaPrompt:
        """Epsilon-greedy: explore a random directive, else exploit the best mean."""
        items = list(self.prompts.values())
        # Only exploit among directives that have been tried at least once.
        tried = [m for m in items if m.n_uses > 0]
        if not tried or self.rng.random() < self.epsilon:
            choice = self.rng.choice(items)
        else:
            choice = max(tried, key=lambda m: (m.mean_aggregate, m.n_uses))
        self.last_id = choice.id
        return choice

    def record(self, meta_id: str, aggregate: float) -> None:
        """Credit a program's fitness back to the directive that guided it."""
        mp = self.prompts.get(meta_id)
        if mp is not None:
            mp.update(aggregate)

    def best(self) -> Optional[MetaPrompt]:
        tried = [m for m in self.prompts.values() if m.n_uses > 0]
        return max(tried, key=lambda m: m.mean_aggregate) if tried else None

    def __len__(self) -> int:
        return len(self.prompts)
