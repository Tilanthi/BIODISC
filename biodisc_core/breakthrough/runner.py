"""Breakthrough discovery runner — invokes all modalities, converges, ranks.

The integration point for the V9.0 rebuild. Runs every discovery modality
(bridge, contradiction, anomaly-in-context, re-mining), collects candidates into
a shared pool, and the ConvergenceScorer flags candidates that >= N independent
methods agree on as high-potential. The survivors flow through the existing
6-layer validation + replication anchor (item 6) as the final gate.

V9.0e: the re-mining connectors (TCGA GDC, AlphaFold EBI) are now WIRED IN —
the runner can actually download real data, run DE, and mine anomalies on
fresh datasets (not just log framework targets).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .candidate import CandidatePool, DiscoveryCandidate
from .convergence import ConvergenceScorer
from .bridge_engine import detect_bridges
from .contradiction_detector import detect_contradictions
from .anomaly_context import detect_anomaly_candidates

logger = logging.getLogger(__name__)


def _de_to_gene_results(de_analysis) -> List[Dict]:
    """Convert a DE analysis result object to the gene_results format the anomaly
    miner expects (full significant set, not just top-20)."""
    return [
        {"gene_symbol": r.gene_symbol, "log2_fold_change": r.log2_fold_change,
         "p_value": r.p_value, "fdr_p_value": r.fdr_p_value,
         "regulation": getattr(r, "regulation", None) or (
             "up" if (r.log2_fold_change or 0) >= 0 else "down")}
        for r in (de_analysis.results or []) if getattr(r, "significant", False)
    ]


def run_remining_with_connectors(
    tcga_cancer_types: Optional[List[str]] = None,
    alphafold_ids: Optional[List[str]] = None,
    prior_directions: Optional[Dict] = None,
    dry_run: bool = True,
) -> List[DiscoveryCandidate]:
    """Run the data connectors (TCGA, AlphaFold) and produce data-driven candidates.

    This is the REAL re-mining path (item 2): actually downloads data from TCGA
    GDC / AlphaFold EBI, runs analysis, and produces DiscoveryCandidates — not
    just framework target descriptions.

    Args:
        tcga_cancer_types: TCGA cancer types to mine (default: ['BRCA']).
        alphafold_ids: UniProt IDs for AlphaFold disorder profiles.
        prior_directions: gene->dataset->direction map for anomaly context.
        dry_run: if True, connectors return synthetic data (no network).

    Returns: list of data-driven DiscoveryCandidates.
    """
    candidates: List[DiscoveryCandidate] = []
    prior = prior_directions or {}

    # --- TCGA: download bulk RNA-seq, run DE, mine anomalies ---
    cancer_types = tcga_cancer_types or ["BRCA"]
    for ctype in cancer_types:
        try:
            from .connectors import fetch_tcga_expression
            expr, genes, labels = fetch_tcga_expression(ctype, dry_run=dry_run)
            if expr is None or len(genes) < 100:
                logger.warning("TCGA %s: no data returned", ctype)
                continue
            logger.info("TCGA %s: %d genes x %d samples — running DE", ctype, len(genes), len(labels))
            # Run the existing DE pipeline on the TCGA data
            from biodisc_core.fixed_pipeline.differential_expression import (
                create_differential_expression_analyzer)
            de = create_differential_expression_analyzer().perform_differential_expression_analysis(
                expr, genes, labels, f"remining_tcga_{ctype}", f"TCGA-{ctype}")
            # Mine anomalies on the TCGA DE results
            gene_results = _de_to_gene_results(de)
            tcga_cands = detect_anomaly_candidates(
                gene_results=gene_results, prior_directions=prior,
                dataset_id=f"TCGA-{ctype}")
            for c in tcga_cands:
                c.methods = ["remining_tcga"]
                c.source_datasets = [f"TCGA-{ctype}"]
                c.data_backed = True  # real data → outranks conceptual candidates
                c.evidence["tcga_cancer_type"] = ctype
                c.evidence["n_significant_genes"] = de.significant_genes
            candidates.extend(tcga_cands)
            logger.info("TCGA %s re-mining: %d anomaly candidates (from %d significant genes)",
                        ctype, len(tcga_cands), de.significant_genes)
        except Exception as e:  # noqa: BLE001
            logger.warning("TCGA %s re-mining failed (non-fatal): %s", ctype, e)

    # --- AlphaFold: fetch disorder profiles, find high-disorder proteins ---
    af_ids = alphafold_ids or ["P04637", "P01106", "P00533", "P42345"]
    try:
        from .connectors import create_alphafold_connector
        af = create_alphafold_connector()
        profiles = []
        for uid in af_ids:
            try:
                p = af.fetch_prediction(uid)
            except Exception:  # noqa: BLE001
                continue  # 404 or network error → skip
            if p and getattr(p, "found", False):
                profiles.append(p)
        if len(profiles) >= 2:
            # Cross-protein comparison
            try:
                comparison = af.compare_proteins(profiles)
            except Exception:  # noqa: BLE001
                comparison = None
            for p in profiles:
                frac = getattr(p, "disordered_fraction", 0.0)
                if frac > 0.3:
                    candidates.append(DiscoveryCandidate(
                        kind="remining_finding",
                        claim=(f"{p.uniprot_id} is {frac:.0%} intrinsically disordered "
                               f"({len(getattr(p, 'disordered_regions', []))} regions) — "
                               f"potential novel regulatory element"),
                        gene=p.uniprot_id,
                        evidence={
                            "source": "AlphaFold", "disordered_fraction": frac,
                            "n_disordered_regions": len(getattr(p, "disordered_regions", [])),
                            "cross_protein_comparison": comparison is not None,
                        },
                        methods=["remining_alphafold"],
                        novelty=0.5, importance=0.6, surprise=min(1.0, frac),
                        testable_with_existing_data=False,
                        data_backed=True,
                    ))
        logger.info("AlphaFold re-mining: %d candidates from %d proteins",
                    len([c for c in candidates if "remining_alphafold" in c.methods]),
                    len(profiles))
    except Exception as e:  # noqa: BLE001
        logger.warning("AlphaFold re-mining failed (non-fatal): %s", e)

    return candidates


def run_breakthrough_discovery(
    literature_gate=None,
    de_results: Optional[Dict] = None,
    prior_directions: Optional[Dict] = None,
    dataset_id: str = "",
    gene_results: Optional[List] = None,
    text_corpus: Optional[str] = None,
    min_convergence: int = 3,
    run_connectors: bool = False,
    connector_dry_run: bool = True,
    tcga_cancer_types: Optional[List[str]] = None,
    alphafold_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Run all discovery modalities, converge, and return ranked candidates.

    Args:
        run_connectors: if True, call the TCGA/AlphaFold connectors for real
            data-driven re-mining (item 2). If False, use framework targets only.
        connector_dry_run: dry_run mode for the connectors (no network).

    Returns:
        {"pool_size": N, "high_potential": [...], "all_ranked": [...]}
    """
    pool = CandidatePool()

    # Item 1: cross-domain bridge engine
    pool.add_all(detect_bridges(literature_gate))

    # Item 3: literature-claim contradiction detector
    pool.add_all(detect_contradictions(text_corpus, literature_gate))

    # Item 4: anomaly-in-context (from a DE result if available)
    if de_results or gene_results:
        pool.add_all(detect_anomaly_candidates(
            de_results, prior_directions, dataset_id, gene_results))

    # Item 2: re-mining — real connectors (if requested) or framework targets
    if run_connectors:
        pool.add_all(run_remining_with_connectors(
            tcga_cancer_types=tcga_cancer_types,
            alphafold_ids=alphafold_ids,
            prior_directions=prior_directions,
            dry_run=connector_dry_run))
    else:
        from .remining import detect_remining_candidates
        pool.add_all(detect_remining_candidates())

    # Item 5: convergence scoring
    scorer = ConvergenceScorer(min_methods=min_convergence)
    ranked = scorer.score_pool(pool)

    high = [c for c in ranked if c.high_potential]
    logger.info("breakthrough runner: %d candidates, %d high-potential (>= %d methods)",
                len(pool), len(high), min_convergence)

    return {
        "pool_size": len(pool),
        "high_potential": high,
        "all_ranked": ranked,
    }
