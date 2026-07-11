"""Initial evolvable DE program (the seed for evolution).

This is the current fixed-pipeline method — a Student's t-test (pooled
variance) — expressed as evolvable source code. Evolution will mutate this
source via LLM-proposed diffs to find more robust statistics.
"""

# Contract for ALL evolved DE programs:
#   - define `def score(expression, labels)`
#   - expression: np.ndarray shape (n_genes, n_samples)
#   - labels: np.ndarray shape (n_samples,), values in {0 (control), 1 (treatment)}
#   - return: 1D np.ndarray shape (n_genes,), per-gene DE score (HIGHER = more DE)
SEED_DE_PROGRAM = '''\
import numpy as np
from scipy import stats


def score(expression, labels):
    """Per-gene differential-expression score (Student's t-test, pooled var).

    Higher score = more differentially expressed. This is the SEED method
    (the fixed pipeline's statistic); evolution mutates it for robustness.
    """
    treat = labels == 1
    ctrl = labels == 0
    n_genes = expression.shape[0]
    out = np.zeros(n_genes, dtype=float)
    for i in range(n_genes):
        t, _ = stats.ttest_ind(expression[i, treat], expression[i, ctrl])
        out[i] = 0.0 if t != t else abs(t)
    return out
'''


def get_seed_program() -> str:
    """Return the initial DE program source."""
    return SEED_DE_PROGRAM
