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
"""P1.6 — controller loop end-to-end with a scripted improvement.

The proposer returns a real, meaningful diff: t-test (significance) -> fold
change (effect size). On heteroscedastic data the pooled-variance t-test
downweights high-variance DE genes, so ranking by fold change gives a better
AUROC (verified ~0.794 vs ~0.781). The loop must (a) apply the diff,
(b) score it higher, (c) archive it, (d) report it as the new best.
"""
from biodisc_core.evolution.controller import EvolutionController
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark


# Replace the t-test scoring loop with a vectorized fold-change score.
FC_DIFF = (
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


def _hard_case():
    return make_de_benchmark(
        n_genes=400, n_samples=24, n_de=40, seed=1,
        effect_size=1.0, noise="heteroscedastic",
    )


def test_controller_finds_improvement_via_scripted_diff():
    proposer = lambda system, user: FC_DIFF  # noqa: E731
    ctrl = EvolutionController(_hard_case(), proposer)
    seed_agg = ctrl.seed_score.aggregate

    result = ctrl.run(generations=1, attempts_per_generation=1)

    assert result.best_score.aggregate > seed_agg, (
        f"fold-change should beat t-test on heteroscedastic data: "
        f"best={result.best_score.aggregate} seed={seed_agg}"
    )
    assert "mean(axis=1)" in result.best_source
    assert len(result.genealogy) >= 2  # seed + improved program
    assert result.improvement > 0


def test_controller_rejects_garbage_without_crashing():
    proposer = lambda system, user: "this is not valid code or diffs"  # noqa: E731
    ctrl = EvolutionController(_hard_case(), proposer)
    log = ctrl.step(1)
    assert log.accepted is False
    assert log.error is not None
    # archive unchanged: only the seed is present
    assert len(ctrl.db.all_programs()) == 1


def test_controller_rejects_broken_program():
    # A diff that produces syntactically broken code.
    proposer = lambda system, user: (  # noqa: E731
        "<<< SEARCH\nreturn out\n===\nreturn ( broken syntax (((\n>>> REPLACE"
    )
    ctrl = EvolutionController(_hard_case(), proposer)
    log = ctrl.step(1)
    assert log.accepted is False
