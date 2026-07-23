"""Cross-domain Bridge Detection Engine (rebuild item 1 — the top recommendation).

Evidence: CRISPR (bacterial immunity -> gene editing), optogenetics (algal opsins
-> neural control), PCR, immune checkpoint therapy (T-cell biology -> oncology),
ubiquitin-proteasome — all 5 were conceptual bridges where the pieces already
existed *separately* in different fields; the breakthrough was the CONNECTION.
Uzzi's atypical-combinations work quantifies that injecting atypical knowledge
into a conventional framework correlates with highest impact.

This engine maintains structured representations of distant fields (their key
mechanisms + unsolved problems) and surfaces "Field A's mechanism X could address
Field B's problem Y" bridges, ranked by novelty (PubMed-absence — so under-
explored bridges surface over well-trodden ones like CRISPR->editing) x
importance x surprise. Fully computational; needs no new data or wet lab.

First version (V9.0): curated field representations + concept-overlap scoring +
PubMed-novelty check. Richer embeddings/analogies are follow-up.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .candidate import DiscoveryCandidate

logger = logging.getLogger(__name__)

# Curated representations of distant fields. Each field has MECHANISMS (things it
# discovered/how it works) and PROBLEMS (things it needs solved). Bridges connect
# a mechanism in one field to a problem in another. Curated from the landmark
# breakthrough evidence (CRISPR, optogenetics, checkpoint therapy, etc.) so the
# engine can both VALIDATE known bridges (they appear) and surface novel ones.
FIELDS: Dict[str, Dict] = {
    "microbiology": {
        "mechanisms": [
            {"name": "CRISPR-Cas sequence-specific DNA cleavage",
             "concepts": ["crispr", "cas", "dna", "cleavage", "sequence", "specific", "adaptive", "immunity"],
             "analogy": "programmable DNA cutting"},
            {"name": "microbial channelrhodopsins (light-gated ion channels)",
             "concepts": ["channelrhodopsin", "light", "ion", "channel", "membrane", "depolarization"],
             "analogy": "light-controlled cell activation"},
            {"name": "bacterial quorum sensing",
             "concepts": ["quorum", "autoinducer", "population", "density", "signaling"],
             "analogy": "population-density-dependent collective behavior"},
            {"name": "bacteriophage lysin cell-wall degradation",
             "concepts": ["phage", "lysin", "cell", "wall", "degradation", "peptidoglycan"],
             "analogy": "enzymatic cell-wall disruption"},
            {"name": " restriction endonucleases (sequence-specific DNA cutting)",
             "concepts": ["restriction", "nuclease", "sequence", "specific", "dna", "cutting"],
             "analogy": "sequence-specific DNA cutting"},
        ],
        "problems": [
            {"name": "antibiotic-resistant bacterial infections",
             "concepts": ["resistance", "antibiotic", "pathogen", "bacterial", "infection"]},
            {"name": "detecting specific DNA sequences in the field",
             "concepts": ["detection", "diagnostic", "sequence", "specific", "dna"]},
        ],
    },
    "neuroscience": {
        "problems": [
            {"name": "precise cell-type-specific control of neural activity",
             "concepts": ["cell", "type", "specific", "control", "neuron", "activity", "precision", "activation"]},
            {"name": "mapping full neural connectomes at scale",
             "concepts": ["connectome", "mapping", "circuit", "neuron", "synapse"]},
        ],
        "mechanisms": [
            {"name": "action potential / membrane depolarization",
             "concepts": ["action", "potential", "membrane", "depolarization", "ion", "voltage"]},
        ],
    },
    "immunology": {
        "mechanisms": [
            {"name": "T-cell immune checkpoints (CTLA4/PD1)",
             "concepts": ["t", "cell", "checkpoint", "ctla4", "pd1", "inhibition", "immune", "activation"],
             "analogy": "releasing immune brakes"},
            {"name": "monoclonal antibody epitope specificity",
             "concepts": ["antibody", "specific", "epitope", "binding", "monoclonal", "recognition"],
             "analogy": "targeted molecular recognition"},
            {"name": "CAR T-cell retargeting",
             "concepts": ["car", "t", "cell", "retargeting", "receptor", "antigen", "specific"],
             "analogy": "redirecting immune cells to a target"},
        ],
        "problems": [
            {"name": "tumor immune evasion",
             "concepts": ["tumor", "cancer", "immune", "evasion", "escape", "recognition"]},
            {"name": "targeting autoimmune disease without broad immunosuppression",
             "concepts": ["autoimmune", "specific", "targeting", "immunosuppression", "tolerance"]},
        ],
    },
    "cancer_oncology": {
        "problems": [
            {"name": "targeted therapy for tumor-specific vulnerabilities",
             "concepts": ["targeted", "therapy", "tumor", "specific", "vulnerability", "oncogene"]},
            {"name": "tumor heterogeneity and drug resistance",
             "concepts": ["heterogeneity", "resistance", "drug", "tumor", "subclone"]},
            {"name": "undruggable protein targets",
             "concepts": ["undruggable", "target", "protein", "drug", "binding", "pocket"]},
        ],
        "mechanisms": [
            {"name": "oncogene addiction",
             "concepts": ["oncogene", "addiction", "dependence", "cancer", "cell"]},
            {"name": "tumor angiogenesis (VEGF)",
             "concepts": ["angiogenesis", "vegf", "blood", "vessel", "tumor"]},
        ],
    },
    "structural_biology": {
        "mechanisms": [
            {"name": "AlphaFold predicted protein structures",
             "concepts": ["structure", "prediction", "protein", "folding", "alphafold", "3d"],
             "analogy": "predicted 3D structures at genome scale"},
            {"name": "cryo-EM density maps",
             "concepts": ["cryo", "em", "density", "structure", "resolution", "complex"],
             "analogy": "near-atomic structures of large complexes"},
        ],
        "problems": [
            {"name": "identifying druggable binding pockets",
             "concepts": ["binding", "pocket", "drug", "site", "protein", "structure"]},
            {"name": "understanding dynamic conformational changes",
             "concepts": ["conformational", "dynamic", "motion", "protein", "structure"]},
        ],
    },
    "gene_editing_delivery": {
        "problems": [
            {"name": "precise in-vivo DNA editing",
             "concepts": ["dna", "editing", "precise", "in", "vivo", "genome", "correction"]},
            {"name": "targeted delivery to specific tissues",
             "concepts": ["delivery", "targeted", "tissue", "specific", "vector", "aav"]},
        ],
        "mechanisms": [
            {"name": "AAV tissue-specific serotypes",
             "concepts": ["aav", "serotype", "tissue", "specific", "delivery", "vector"],
             "analogy": "tissue-specific delivery vehicles"},
        ],
    },
}

# Fields whose problems are inherently high-impact (cancer, neuro, immune).
HIGH_IMPACT_PROBLEM_FIELDS = {"cancer_oncology", "neuroscience", "immunology"}


def _overlap(a: List[str], b: List[str]) -> int:
    return len(set(a) & set(b))


def _novelty(mech: Dict, problem: Dict, literature_gate) -> float:
    """1 - PubMed similarity of the bridge claim. Neutral 0.5 if no gate."""
    if literature_gate is None:
        return 0.5
    try:
        claim = f"{mech['name']} {problem['name']}"
        verdict = literature_gate.assess(claim)
        if getattr(verdict, "status", "") == "retrieval_failed":
            return 0.5
        sim = getattr(verdict, "max_similarity", 0.0) or 0.0
        return max(0.0, min(1.0, 1.0 - sim))
    except Exception as e:  # noqa: BLE001
        logger.debug("bridge novelty check failed: %s", e)
        return 0.5


def _importance(problem_field: str, mech: Dict, problem: Dict) -> float:
    base = 0.7 if problem_field in HIGH_IMPACT_PROBLEM_FIELDS else 0.4
    # analogies that have historically yielded tools get a bump
    if mech.get("analogy"):
        base = min(1.0, base + 0.1)
    return base


def detect_bridges(literature_gate=None, min_overlap: int = 1) -> List[DiscoveryCandidate]:
    """Surface cross-domain bridge candidates ranked by novelty x importance x surprise.

    For each (field A mechanism, field B problem) pair with concept overlap, emit a
    DiscoveryCandidate. Novelty comes from PubMed (so well-trodden bridges like
    CRISPR->editing rank LOW; under-explored ones rank HIGH). Returns candidates
    sorted by EV descending.
    """
    candidates: List[DiscoveryCandidate] = []
    fields = list(FIELDS.items())
    for i, (fa_name, fa) in enumerate(fields):
        for j, (fb_name, fb) in enumerate(fields):
            if i == j:
                continue
            for mech in fa.get("mechanisms", []):
                for problem in fb.get("problems", []):
                    ov = _overlap(mech.get("concepts", []), problem.get("concepts", []))
                    if ov < min_overlap:
                        continue
                    novelty = _novelty(mech, problem, literature_gate)
                    importance = _importance(fb_name, mech, problem)
                    surprise = min(1.0, 0.2 + ov / 3.0)
                    claim = (f"{fa_name}'s {mech['name']} could address "
                             f"{fb_name}'s problem: {problem['name']}")
                    candidates.append(DiscoveryCandidate(
                        kind="cross_domain_bridge", claim=claim,
                        field_a=fa_name, field_b=fb_name,
                        evidence={"mechanism": mech["name"], "problem": problem["name"],
                                  "concept_overlap": ov, "analogy": mech.get("analogy", "")},
                        methods=["bridge"], novelty=novelty, importance=importance,
                        surprise=surprise, testable_with_existing_data=True,
                    ))
    candidates.sort(key=lambda c: c.ev, reverse=True)
    logger.info("bridge engine: %d cross-domain candidates", len(candidates))
    return candidates
