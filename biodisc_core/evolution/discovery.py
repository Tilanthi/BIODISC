"""Phase 3 — Discovery programs: evolvable code that emits quantitative claims.

A discovery program is source defining::

    def discover(expression, labels, gene_symbols=None) -> list[dict]

Each returned claim dict carries a gene, a direction, an effect size, a 95% CI,
and a p-value. This is the Phase 3 generalization of the Phase 1-2 DE *method*:
instead of only scoring genes, the program commits to CLAIMS with uncertainty.

Fitness is anchored on REPLICATION (replication.py): claims made on a discovery
cohort must hold on an independent cohort. The program never sees ground truth.

SECURITY: compile_discover_program execs source (sandbox in production).
"""
import ast
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import numpy as np

DISCOVERY_PROGRAM_CONTRACT = (
    "Source must define `def discover(expression, labels, gene_symbols=None):` "
    "returning a list of claim dicts with keys: gene_index (int), direction "
    "(+1/-1), effect_size (float), ci_low (float), ci_high (float), p_value (float)."
)

CLAIM_KEYS = {"gene_index", "direction", "effect_size", "ci_low", "ci_high", "p_value"}


@dataclass
class DiscoveryClaim:
    gene_index: int
    direction: int            # +1 up in treatment, -1 down
    effect_size: float
    ci_low: float
    ci_high: float
    p_value: float
    gene_symbol: Optional[str] = None


@dataclass
class DiscoveryResult:
    """The output of running a discovery program on one dataset."""
    dataset_id: str
    claims: List[DiscoveryClaim]
    method_program_id: Optional[str] = None     # link to evolved DE-method genealogy
    discovery_program_id: Optional[str] = None  # link to this discovery program

    @property
    def n_claims(self) -> int:
        return len(self.claims)


def validate_discover_source(source: str) -> bool:
    """Static check: source parses and defines a top-level ``discover`` function."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(n, ast.FunctionDef) and n.name == "discover"
        for n in tree.body
    )


def _coerce_claims(raw) -> List[DiscoveryClaim]:
    """Validate + coerce raw claim dicts into DiscoveryClaim."""
    out = []
    for item in (raw or []):
        if not isinstance(item, dict):
            continue
        if not CLAIM_KEYS.issubset(item.keys()):
            continue
        try:
            out.append(DiscoveryClaim(
                gene_index=int(item["gene_index"]),
                direction=int(item["direction"]),
                effect_size=float(item["effect_size"]),
                ci_low=float(item["ci_low"]),
                ci_high=float(item["ci_high"]),
                p_value=float(item["p_value"]),
            ))
        except (TypeError, ValueError):
            continue
    return out


def compile_discover_program(source: str) -> Callable:
    """Compile discovery source into a callable ``discover(...)``.

    Raises ValueError if the source is invalid or does not define ``discover``.
    """
    if not validate_discover_source(source):
        raise ValueError(f"Invalid discovery program. {DISCOVERY_PROGRAM_CONTRACT}")
    namespace: dict = {"np": np, "__name__": "discovery_program"}
    exec(compile(source, "<discovery_program>", "exec"), namespace)  # noqa: S102
    fn = namespace.get("discover")
    if not callable(fn):
        raise ValueError(f"discovery program did not define callable `discover`. {DISCOVERY_PROGRAM_CONTRACT}")
    return fn


def run_discover_program(fn, expression, labels, gene_symbols=None,
                         dataset_id: str = "benchmark") -> DiscoveryResult:
    """Run a compiled discover() and coerce its claims into a DiscoveryResult."""
    raw = fn(expression, labels, gene_symbols)
    claims = _coerce_claims(raw)
    # Attach gene symbols if provided and in range.
    if gene_symbols is not None:
        for c in claims:
            if 0 <= c.gene_index < len(gene_symbols):
                c.gene_symbol = gene_symbols[c.gene_index]
    return DiscoveryResult(dataset_id=dataset_id, claims=claims)


# The seed discovery program: composes the Phase-1 t-test method with claim
# construction (effect size + 95% CI + p-value). Evolution mutates the scoring
# AND/OR the claim construction toward replication fitness.
SEED_DISCOVERY_PROGRAM = '''\
import numpy as np
from scipy import stats


def discover(expression, labels, gene_symbols=None):
    """Emit top differential-expression claims with effect size + 95% CI + p.

    Ranks genes by |t| (Student's t-test), then constructs a claim for each of
    the top-K genes. SEED discovery program; evolution mutates it.
    """
    treat = labels == 1
    ctrl = labels == 0
    n_genes = expression.shape[0]
    K = min(10, n_genes)
    scores = np.zeros(n_genes)
    pvals = np.ones(n_genes)
    for i in range(n_genes):
        t, p = stats.ttest_ind(expression[i, treat], expression[i, ctrl])
        t = 0.0 if t != t else t
        scores[i] = abs(t)
        pvals[i] = 1.0 if p != p else p
    top = np.argsort(-scores)[:K]
    claims = []
    for i in top:
        a = expression[i, treat]
        b = expression[i, ctrl]
        eff = float(a.mean() - b.mean())
        va = float(a.var(ddof=1)) if len(a) > 1 else 1.0
        vb = float(b.var(ddof=1)) if len(b) > 1 else 1.0
        se = float(np.sqrt(va / len(a) + vb / len(b)))
        df = len(a) + len(b) - 2
        tcrit = float(stats.t.ppf(0.975, df)) if df > 0 else 1.96
        half = tcrit * se
        claims.append({
            "gene_index": int(i),
            "direction": 1 if eff > 0 else -1,
            "effect_size": eff,
            "ci_low": eff - half,
            "ci_high": eff + half,
            "p_value": float(pvals[i]),
        })
    return claims
'''


def get_seed_discovery_program() -> str:
    return SEED_DISCOVERY_PROGRAM
