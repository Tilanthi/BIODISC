"""P2.2 — co-evolved meta-prompts."""
import random

from biodisc_core.evolution.meta_prompt import MetaPromptArchive, MetaPrompt
from biodisc_core.evolution.controller import EvolutionController
from biodisc_core.fixed_pipeline.benchmark import make_de_benchmark


def test_record_updates_empirical_mean():
    arch = MetaPromptArchive(prompts=["A", "B"], rng=random.Random(0), epsilon=0.0)
    a_id = arch.prompts[next(i for i, m in arch.prompts.items() if m.text == "A")].id
    arch.record(a_id, 0.6)
    arch.record(a_id, 0.8)
    assert arch.prompts[a_id].n_uses == 2
    assert abs(arch.prompts[a_id].mean_aggregate - 0.7) < 1e-9


def test_sample_returns_a_directive_and_sets_last_id():
    arch = MetaPromptArchive(prompts=["A", "B"], rng=random.Random(0), epsilon=1.0)
    mp = arch.sample()
    assert isinstance(mp, MetaPrompt)
    assert arch.last_id == mp.id


def test_best_picks_higher_empirical_mean():
    arch = MetaPromptArchive(prompts=["A", "B"], rng=random.Random(0), epsilon=0.0)
    ids = {m.text: m.id for m in arch.prompts.values()}
    arch.record(ids["A"], 0.5)
    arch.record(ids["B"], 0.9)
    assert arch.best().text == "B"


def test_epsilon_zero_exploits_best_tried():
    arch = MetaPromptArchive(prompts=["A", "B", "C"], rng=random.Random(0), epsilon=0.0)
    ids = {m.text: m.id for m in arch.prompts.values()}
    arch.record(ids["A"], 0.5)
    arch.record(ids["B"], 0.9)
    # epsilon=0 and tried prompts exist -> always returns the best (B).
    for _ in range(10):
        assert arch.sample().text == "B"


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


def test_controller_credits_meta_prompt_on_accept():
    case = make_de_benchmark(n_genes=300, n_samples=24, n_de=30, seed=1,
                             effect_size=1.0, noise="heteroscedastic")
    proposer = lambda system, user: FC_DIFF  # noqa: E731
    ctrl = EvolutionController(case, proposer)
    before_uses = sum(m.n_uses for m in ctrl.meta_archive.prompts.values())
    ctrl.step(1)
    after_uses = sum(m.n_uses for m in ctrl.meta_archive.prompts.values())
    assert after_uses == before_uses + 1, "accepted program must credit its meta-prompt"
    assert ctrl.meta_archive.best() is not None
