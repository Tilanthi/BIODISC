"""Provider-agnostic LLM proposer for the evolutionary loop (AlphaEvolve).

AlphaEvolve is model-agnostic: it used Gemini, but any strong code-capable model
works. This module uses the Anthropic Messages API as a WIRE PROTOCOL and points
it at whatever Anthropic-compatible gateway is configured via environment:

    ANTHROPIC_BASE_URL     -> e.g. https://api.z.ai/api/anthropic  (GLM via z.ai)
    ANTHROPIC_AUTH_TOKEN   -> credential (used by Claude Code itself here)
    ANTHROPIC_API_KEY      -> alternative credential (real Anthropic)

So the SAME code runs against real Anthropic OR GLM (z.ai) OR any other
Anthropic-compatible endpoint — "running a different model" is just an env-var
change. The default model is GLM (glm-4.6), overridable via
BIODISC_EVOLUTION_MODEL. The client is injectable for deterministic tests.
"""
import os
import random
from typing import Callable, Optional, Sequence


def _extract_text(resp) -> str:
    """Join text blocks from an Anthropic-style Messages response."""
    parts = []
    for block in getattr(resp, "content", []) or []:
        if getattr(block, "type", "") == "text":
            parts.append(getattr(block, "text", ""))
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


class LLMEnsemble:
    """Calls an Anthropic-compatible Messages endpoint, round-robining models."""

    def __init__(
        self,
        client=None,
        models: Optional[Sequence[str]] = None,
        rng: Optional[random.Random] = None,
        max_tokens: int = 1024,
    ):
        self.client = client if client is not None else self._auto_client()
        self.models = list(models) if models is not None else self._default_models()
        if not self.models:
            raise ValueError("at least one model must be configured")
        self.rng = rng or random.Random(0)
        self.max_tokens = max_tokens
        self._idx = 0
        self.last_model: Optional[str] = None

    @staticmethod
    def _auto_client():
        from anthropic import Anthropic
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        api_key = (
            os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or os.environ.get("ANTHROPIC_API_KEY")
        )
        if not api_key:
            raise RuntimeError(
                "No LLM credential found. Set ANTHROPIC_AUTH_TOKEN (or "
                "ANTHROPIC_API_KEY). The endpoint may be ANY Anthropic-compatible "
                "gateway, e.g. GLM via z.ai (ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic)."
            )
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        return Anthropic(**kwargs)

    @staticmethod
    def _default_models():
        env_model = os.environ.get("BIODISC_EVOLUTION_MODEL")
        if env_model:
            return [m.strip() for m in env_model.split(",") if m.strip()]
        # Default: GLM via z.ai (the configured gateway in this environment).
        return ["glm-4.6"]

    def propose(self, system: str, user: str) -> str:
        """Call the model and return its raw text (diffs or full program)."""
        model = self.models[self._idx % len(self.models)]
        self._idx += 1
        self.last_model = model
        resp = self.client.messages.create(
            model=model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _extract_text(resp)


# A proposer is anything callable as (system, user) -> str. This lets tests (and
# a deterministic smoke run) pass a scripted function instead of a live model.
Proposer = Callable[[str, str], str]
