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
"""P2.4 — evaluation cascade: cheap screen -> full -> held-out."""
from biodisc_core.evolution.evaluation_cascade import (
    make_screen_case, cascade_evaluate,
)
from biodisc_core.evolution.controller import EvolutionController
from biodisc_core.evolution.seeds import get_seed_program
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark


def _full():
    return make_de_benchmark(n_genes=400, n_samples=24, n_de=40, seed=1,
                             effect_size=1.0, noise="heteroscedastic")


def test_screen_case_is_smaller_and_independent():
    full = _full()
    sc = make_screen_case(full, n_genes_screen=120)
    assert sc.n_genes <= 120
    assert sc.n_genes < full.n_genes
    assert sc.seed != full.seed


def test_good_method_passes_cascade():
    score = cascade_evaluate(get_seed_program(), _full())
    assert score is not None
    assert score.aggregate > 0.0


def test_bad_method_is_pruned_at_screen():
    # Returns zeros -> AUROC ~0.5 -> below the screen floor -> pruned.
    bad = "def score(expression, labels):\n    import numpy as np\n    return np.zeros(expression.shape[0])\n"
    assert cascade_evaluate(bad, _full(), screen_floor=0.55) is None


def test_controller_with_cascade_prunes_bad_output():
    bad = "def score(expression, labels):\n    import numpy as np\n    return np.zeros(expression.shape[0])\n"
    proposer = lambda system, user: bad  # noqa: E731  (full-program proposal)
    ctrl = EvolutionController(_full(), proposer, use_cascade=True, screen_floor=0.55)
    log = ctrl.step(1)
    assert log.accepted is False
    assert log.error is not None and "cascade" in log.error.lower()
    assert len(ctrl.db.all_programs()) == 1  # only the seed


def test_controller_with_cascade_still_accepts_improvement():
    fc_diff = (
        "<<< SEARCH\n"
        "    n_genes = expression.shape[0]\n"
        "    out = np.zeros(n_genes, dtype=float)\n"
        "    for i in range(n_genes):\n"
        "        t, _ = stats.ttest_ind(expression[i, treat], expression[i, ctrl])\n"
        "        out[i] = 0.0 if t != t else abs(t)\n"
        "    return out\n"
        "===\n"
        "    return np.abs(expression[:, treat].mean(axis=1) - expression[:, ctrl].mean(axis=1))\n"
        ">>> REPLACE"
    )
    proposer = lambda system, user: fc_diff  # noqa: E731
    ctrl = EvolutionController(_full(), proposer, use_cascade=True)
    seed_agg = ctrl.seed_score.aggregate
    result = ctrl.run(generations=1, attempts_per_generation=1)
    assert result.best_score.aggregate > seed_agg
