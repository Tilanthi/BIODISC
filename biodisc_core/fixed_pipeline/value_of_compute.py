"""Value-of-compute gate — rank candidate questions before spending DE/replication.

The discovery loop's selector historically optimized for *realness* (significance +
replication). That is anti-correlated with novelty: the most replicable signals on a
public dataset are the ones the field already published, so the loop kept surfacing
textbook biology (Cyp2e1-in-fatty-liver, etc.). Realness is a *floor*, not the
objective. This module scores each candidate question on the axes that actually
correlate with a paradigm-shifting finding, so the loop can fund only the top-k by
expected value (plus a small exploration slice) instead of spending DE on every
answerable question.

Three axes, each in [0, 1]:

* **novelty** — 1 - literature-similarity, reusing the Gate-2 PubMed TF-cosine
  machinery as a *scorer* (not a pass/fail reject). A question whose substance is
  already blanketing PubMed is low-novelty. Falls back to a neutral 0.5 on
  retrieval failure (never blocks on the network).
* **importance** — a first-gen proxy: does the question touch a hub gene or a
  central pathway (many downstream predictions if confirmed)? Obscure gene, no
  pathway context -> low importance. This is a proxy for a real centrality score
  (STRING/KEGG) that can be wired later.
* **surprise** — how much the likely result would contradict the textbook. A
  confirmatory "which genes differ between tumor and normal" is ~0 surprise; a
  contrarian direction ("does X *decrease* where it is known to increase"), a
  cross-context reversal, or a known gene in an unexpected tissue is high. This
  is the Eureka term and it is shared with the contrarian question generator
  (item 4) so the two stay aligned.

EV = novelty * importance * surprise / cost, where cost ~ log(dataset size).
``fund_candidates`` returns the top-k by EV PLUS a small random exploration slice
of the remainder — the gate *ranks and allocates*, it never silently drops the
long tail (that is the eureka-insurance discipline: a low-EV candidate today could
be the surprise tomorrow).
"""
from __future__ import annotations

import logging
import math
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---- importance vocabulary (first-gen proxy for network centrality) ------------
# Hub genes / central regulators — a finding involving one of these enables many
# downstream predictions, so it is higher-importance than a finding about an
# obscure gene. This is a stand-in for a real STRING/KEGG centrality score.
HUB_GENES = {
    # tumor suppressors / oncogenes
    "TP53", "MYC", "EGFR", "ERBB2", "HER2", "KRAS", "BRAF", "PIK3CA", "PTEN",
    "AKT1", "AKT", "MTOR", "RB1", "CDK4", "CCND1", "BRCA1", "BRCA2", "APC",
    "VHL", "NF1", "NF2", "STAT3", "STAT1", "HIF1A",
    # signaling / metabolism hubs
    "INS", "INSR", "IGF1", "TNF", "IL6", "IL1B", "VEGFA", "TGFB1", "TGF", "NFkB",
    "NFKB1", "MAPK", "MAPK1", "AMPK", "PRKAA1", "SREBF1", "PPARG", "PPARA",
    # epigenetic / chromatin
    "DNMT1", "HDAC1", "KDM1A", "EZH2",
    # housekeeping-but-informative
    "ACTB", "GAPDH", "CD4", "CD8A", "CD19",
}
IMPORTANT_PATHWAY_TERMS = {
    "apoptosis", "cell cycle", "cell-cycle", "cellular senescence", "senescence",
    "insulin signaling", "insulin-signaling", "mtor", "ampk", "p53", "tp53",
    "wnt", "notch", "mapk", "erbb", "pi3k", "jak-stat", "nf-kb", "nfkb",
    "tgf-beta", "tgfb", "hypoxia", "angiogenesis", "epithelial-mesenchymal",
    "emt", "dna damage", "dna-damage", "dna repair", "dna-repair", "autophagy",
    "ferroptosis", "immune checkpoint", "immune-checkpoint", "antigen presentation",
    "inflammatory", "interferon", "wnt/beta-catenin", "glycolysis", "oxidative",
    "unfolded protein response", "upr", "endoplasmic reticulum",
}

# ---- surprise vocabulary (shared with the contrarian question generator) -------
# Direction words. A question that pairs a known gene with the OPPOSITE direction
# of its textbook change is high-surprise. Without a "known direction" database
# (a later-gen feature), we score the *framing*: an explicit contrarian direction,
# a cross-context reversal, or a known gene placed in an unexpected tissue.
DIRECTION_UP = {"increase", "increases", "increased", "up", "upregulat", "higher",
                "elevated", "elevate", "overexpress", "induc", "activat", "raise", "gain"}
DIRECTION_DOWN = {"decrease", "decreases", "decreased", "down", "downregulat", "lower",
                  "reduced", "reduce", "loss", "inhibit", "suppress", "block", "drop", "fall"}
REVERSAL_TERMS = {"reverse", "reverses", "opposite", "contradict", "contrary",
                  "paradox", "unexpected", "surprising", "inconsistent", "break",
                  "violat", "unlike", "whereas", "contrast", "differ between species",
                  "cross-species", "mutually exclusive", "anti-correlat"}

# All-caps tokens that look like gene symbols but aren't. Used by
# ``extract_named_genes`` so the binding gate doesn't treat "DNA"/"FDR"/"GSE" as
# a named gene. Kept conservative — real gene symbols (TP53, MYC, MTOR, ABCB1,
# CYP2E1, MMP2) are 2-7 chars and all-caps, so the exclusion list is the cheap
# way to drop the common non-gene acronyms that share that shape.
NON_GENE_CAPS = {
    "DNA", "RNA", "MRNA", "RRNA", "TRNA", "FDR", "GSE", "GPL", "GEO", "ECM",
    "SNP", "MSI", "ILMN", "HOMO", "HFD", "NCBI", "HUGO", "SRA", "UCSC", "TSS",
    "PCR", "NMR", "BMI", "CNS", "MRI", "DE", "UP", "DOWN", "VS", "LOG", "FC",
    "SD", "SE", "CI", "HR", "OR", "AUC", "ROC", "PCA", "UMAP", "TSNE", "GWAS",
    "ORF", "UTR", "CHR", "Bp", "KDA", "MMR",
}

# Prefixes of sequence/probe/accession identifiers that look gene-shaped but
# aren't (GSE2034, ILMN_1659893, ENSG00000141510, SRR3424567…). No real gene
# symbol starts with these.
_ACCESSION_PREFIXES = ("GSE", "GSM", "GPL", "ILMN", "ENS", "SRR", "ERR",
                       "PXD", "NX", "BC0")


def extract_named_genes(question: str) -> List[str]:
    """Gene symbols explicitly named in the question.

    Matches all-caps alphanumeric tokens of length 2-7 (the shape of real gene
    symbols — TP53, MYC, MTOR, ABCB1, CYP2E1) and drops the common non-gene
    acronyms in :data:`NON_GENE_CAPS`. Used by the question-result binding gate
    (Layer 7) to check that a gene-naming question is actually answered by the
    DE result, not decorative.
    """
    found = set()
    for m in re.findall(r"\b[A-Z][A-Z0-9-]{1,6}\b", question or ""):
        g = m.upper().rstrip("-")          # "DNA-repair" -> "DNA" -> excluded below
        if len(g) < 2 or g in NON_GENE_CAPS:
            continue
        if any(g.startswith(p) for p in _ACCESSION_PREFIXES):  # GSE2034, ILMN_…, ENSG…
            continue
        found.add(g)
    return sorted(found)


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _tokens(text: str) -> List[str]:
    return [t for t in text.lower().split() if t.strip(" ,?.;:'\"()[]/")]


def _importance(question: str) -> float:
    """First-gen importance proxy: hub-gene / central-pathway presence.

    A finding about a hub gene or a central pathway enables more downstream
    predictions than one about an obscure gene, so it is higher EV. Returns a
    smooth [0,1] score rather than a step so ties break gently.
    """
    q = question.lower()
    toks = set(_tokens(question))
    # gene hits (match bare symbols)
    gene_hits = sum(1 for g in HUB_GENES if g.lower() in toks or g.lower() in q)
    # pathway hits (substring, since pathway names are multi-word)
    path_hits = sum(1 for p in IMPORTANT_PATHWAY_TERMS if p in q)
    # importance rises with hits but saturates quickly (one hub is enough to matter)
    return _clamp01(0.15 + 0.45 * (1 - math.exp(-gene_hits)) + 0.40 * (1 - math.exp(-path_hits)))


def _surprise(question: str) -> float:
    """First-gen surprise proxy: contrarian framing / reversal / unexpected context.

    This is the Eureka axis. Confirmatory questions ("which genes differ between X
    and Y") score near the floor. A question that asserts a specific opposite
    direction, a cross-context reversal, or that names a reversal gets boosted.
    """
    q = question.lower()
    score = 0.10  # floor: a real analysis always carries a little surprise potential

    has_up = any(d in q for d in DIRECTION_UP)
    has_down = any(d in q for d in DIRECTION_DOWN)
    # explicit contrarian direction about a named gene is the strongest signal
    if (has_up or has_down):
        # does it name a gene (an ALL-CAPS token or a known hub)? directional
        # claims are only surprising if they're specific.
        names_gene = any(g.lower() in q for g in HUB_GENES) or _names_a_gene(question)
        if names_gene:
            score += 0.45
        else:
            score += 0.10
    # explicit reversal / contradiction language
    if any(t in q for t in REVERSAL_TERMS):
        score += 0.35
    # cross-context comparison (species / state / condition contrasts) where a
    # known relationship could flip
    if any(t in q for t in ("between species", "across species", "mouse vs",
                            "human vs", "versus normal", "vs normal", "between ",
                            "across ")):
        score += 0.10

    return _clamp01(score)


def _names_a_gene(question: str) -> bool:
    """Cheap heuristic: does the question name a specific gene symbol?

    All-caps alphanumeric tokens of length 2-6 (e.g. CYP2E1, ABCB1, MMP2, TP53)
    or an explicit '(SYMBOL)' annotation.
    """
    import re
    if re.search(r"\([A-Z][A-Z0-9-]{1,6}\)", question):
        return True
    for tok in question.replace("(", " ").replace(")", " ").split():
        if len(tok) >= 2 and tok.isupper() and re.fullmatch(r"[A-Z][A-Z0-9-]{1,6}", tok):
            # filter common English all-caps words that appear in questions
            if tok.lower() not in {"dna", "rna", "fdr", "gse", "ecm", "mir", "snp",
                                   "msi", "her", "tnf", "ilmn", "homo"}:
                return True
    return False


def _novelty(question: str, literature_gate) -> float:
    """Novelty = 1 - literature similarity (reuses Gate-2 as a scorer).

    Falls back to a neutral 0.5 on retrieval failure or when no gate is supplied,
    so this never blocks on the network and tests can run offline.
    """
    if literature_gate is None:
        return 0.5
    try:
        verdict = literature_gate.assess(question)
    except Exception as e:  # noqa: BLE001
        logger.debug("novelty scorer: assess() raised (%s); neutral fallback", e)
        return 0.5
    if getattr(verdict, "status", "") == "retrieval_failed":
        return 0.5  # don't reward or penalize on a network failure
    sim = getattr(verdict, "max_similarity", 0.0) or 0.0
    return _clamp01(1.0 - sim)


def _cost(dataset: Optional[dict]) -> float:
    """Compute-cost proxy ~ log2(sample count); >=1. Bigger datasets cost more DE."""
    if not dataset:
        return 1.0
    n = dataset.get("samples") or dataset.get("sample_count") or 0
    try:
        n = int(n)
    except Exception:
        n = 0
    if n <= 1:
        return 1.0
    return 1.0 + math.log2(n)


@dataclass
class QuestionValue:
    question: str
    dataset: Optional[dict]
    novelty: float
    importance: float
    surprise: float
    cost: float
    ev: float
    funded: bool = False
    reason: str = ""

    def as_dict(self) -> dict:
        return {k: (v if not isinstance(v, dict) else dict(v))
                for k, v in self.__dict__.items()}


def score_question(question: str,
                   dataset: Optional[dict] = None,
                   literature_gate=None) -> QuestionValue:
    """Score one question on novelty x importance x surprise / cost."""
    novelty = _novelty(question, literature_gate)
    importance = _importance(question)
    surprise = _surprise(question)
    cost = _cost(dataset)
    ev = (novelty * importance * surprise) / cost if cost > 0 else 0.0
    return QuestionValue(
        question=question, dataset=dataset,
        novelty=round(novelty, 3), importance=round(importance, 3),
        surprise=round(surprise, 3), cost=round(cost, 3), ev=round(ev, 4),
    )


def fund_candidates(scored: List[QuestionValue],
                    top_k: int = 5,
                    exploration_frac: float = 0.15,
                    rng: Optional[random.Random] = None) -> List[QuestionValue]:
    """Return the candidates worth spending DE on: top-k by EV + an exploration slice.

    The exploration slice is a random ``exploration_frac`` of the *non-top-k*
    remainder. This is the eureka-insurance discipline: the gate allocates most
    compute to high-EV (surprising/novel/important) candidates but never goes
    100% exploitation — a low-EV candidate today could carry the surprise the
    scorer can't yet measure.
    """
    rng = rng or random
    ranked = sorted(scored, key=lambda s: s.ev, reverse=True)
    funded = ranked[:max(0, top_k)]
    funded_ids = {id(s) for s in funded}
    remainder = [s for s in ranked if id(s) not in funded_ids]
    n_explore = int(round(len(remainder) * max(0.0, exploration_frac)))
    exploration = rng.sample(remainder, min(n_explore, len(remainder))) if remainder else []
    for s in funded:
        s.funded = True
        s.reason = "top_k_by_ev"
    for s in exploration:
        s.funded = True
        s.reason = "exploration_slice"
    for s in ranked:
        if not s.funded:
            s.reason = "low_ev_deprioritized"
    # preserve original input order among funded for stable loop behavior
    funded_set = {id(s) for s in funded + exploration}
    return [s for s in scored if id(s) in funded_set]
