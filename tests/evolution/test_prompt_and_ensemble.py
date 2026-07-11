"""P1.4 + P1.5 — prompt sampler + provider-agnostic LLM ensemble."""
import random
import types

from biodisc_core.evolution.prompt_sampler import build_evolution_prompt, SYSTEM_PROMPT
from biodisc_core.evolution.llm_ensemble import LLMEnsemble
from biodisc_core.evolution.program_db import ArchivedProgram


def _arch(agg, src="def score(e, l):\n    return e.sum(axis=1)\n"):
    return ArchivedProgram(
        program_id="abc123", source=src, aggregate=agg, auroc=agg,
        replicate_concordance=agg, generation=0, parent_id=None,
        complexity=10, bucket=0,
    )


def test_prompt_contains_parent_and_contract():
    parent = _arch(0.82)
    sys_p, user = build_evolution_prompt(parent, [_arch(0.80)], generation=3, rng=random.Random(1))
    assert "0.82" in user
    assert "def score(e, l)" in user
    assert "GENERATION 3" in user
    assert "diff blocks" in sys_p.lower() or "search" in sys_p.lower()
    assert "<<< SEARCH" in sys_p


def test_prompt_deterministic_given_seed():
    parent = _arch(0.8)
    _, u1 = build_evolution_prompt(parent, [], 1, random.Random(7))
    _, u2 = build_evolution_prompt(parent, [], 1, random.Random(7))
    assert u1 == u2  # stochastic style hint is seeded


# --- LLM ensemble with a fake client (no network) ---

class _FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _FakeResp:
    def __init__(self, text):
        self.content = [_FakeBlock(text)]


class _FakeMessages:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def create(self, **kw):
        self.calls.append(kw)
        return self.replies.pop(0)


class _FakeClient:
    def __init__(self, replies):
        self.messages = _FakeMessages(replies)


def test_ensemble_propose_returns_model_text_and_records_model():
    client = _FakeClient([_FakeResp("<<< SEARCH\nx\n===\ny\n>>> REPLACE")])
    ens = LLMEnsemble(client=client, models=["glm-4.6"])
    out = ens.propose("sys", "usr")
    assert out == "<<< SEARCH\nx\n===\ny\n>>> REPLACE"
    assert ens.last_model == "glm-4.6"
    assert client.messages.calls[0]["model"] == "glm-4.6"
    assert client.messages.calls[0]["system"] == "sys"


def test_ensemble_round_robins_models():
    client = _FakeClient([_FakeResp("a"), _FakeResp("b")])
    ens = LLMEnsemble(client=client, models=["m1", "m2"])
    ens.propose("s", "u")
    ens.propose("s", "u")
    assert [c["model"] for c in client.messages.calls] == ["m1", "m2"]


def test_default_model_from_env(monkeypatch):
    monkeypatch.setenv("BIODISC_EVOLUTION_MODEL", " some-model , other ")
    assert LLMEnsemble._default_models() == ["some-model", "other"]


def test_auto_client_raises_without_credential(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        LLMEnsemble._auto_client()
        assert False, "expected RuntimeError without a credential"
    except RuntimeError as e:
        assert "credential" in str(e).lower()
