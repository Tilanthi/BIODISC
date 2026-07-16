"""
Specific Biological Questions Generator

Generates specific, novel biological questions instead of generic topics.

This addresses peer review criticism that questions like "patient stratification"
are too broad and represent well-established fields.

Each question should be:
1. SPECIFIC to a biological mechanism or context
2. NOVEL (not well-established)
3. TESTABLE with available data
4. MEANINGFUL (advances understanding)
"""

import logging
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SpecificQuestionsGenerator:
    """
    Generates specific, novel biological questions for genuine discovery.

    Replaces generic questions with specific, testable hypotheses.
    """

    def __init__(self):
        logger.info("❓ Specific Questions Generator initialized")

    def generate_specific_questions(self) -> List[str]:
        """
        Generate specific biological questions that represent genuine novelty.

        Returns:
            List of specific biological questions
        """

        questions = [
            # CANCER BIOLOGY - Specific mechanisms
            "How does BRCA1 mutation status affect response to PARP inhibitors in triple-negative breast cancer?",

            # TRANSCRIPTIONAL REGULATION - Specific factors
            "Does STAT3 activation differ between IL-6 treated and untreated glioblastoma cells?",

            # METABOLISM - Specific pathways
            "How does AMPK activation alter glycolytic flux in response to glucose deprivation?",

            # APOPTOSIS - Specific regulators
            "What is the role of BCL2 family member interactions in mitochondrial outer membrane permeabilization?",

            # SIGNALING - Specific pathways
            "How does EGFR inhibition alter downstream MAPK/ERK signaling in lung adenocarcinoma?",

            # EPIGENETICS - Specific modifications
            "How does DNA methylation at the MLH1 promoter differ between MSI-H and MSS colorectal cancers?",

            # PROTEOSTASIS - Specific stressors
            "How does heat shock protein 70 (HSP70) expression correlate with proteasome inhibition sensitivity?",

            # ANGIOGENESIS - Specific factors
            "Does VEGFA expression differ between hypoxic and normoxic conditions in endothelial cells?",

            # INFLAMMATION - Specific cytokines
            "How does TNF-alpha exposure alter NF-κB nuclear translocation in macrophages?",

            # CELL CYCLE - Specific checkpoints
            "What is the relationship between p21 levels and G1/S checkpoint activation in DNA-damaged cells?",

            # DIFFERENTIATION - Specific lineages
            "How does MYOD expression fluctuate during myoblast differentiation vs proliferation?",

            # AUTOPHAGY - Specific regulators
            "Does mTOR inhibition alter LC3-II formation in amino acid starved cells?",

            # SENESCENCE - Specific markers
            "How does beta-galactosidase activity differ between replicative and oncogene-induced senescence?",

            # METASTASIS - Specific proteases
            "Does MMP2 expression correlate with invasiveness in triple-negative vs HER2+ breast cancer?",

            # DRUG RESISTANCE - Specific mechanisms
            "How does ABCB1 (MDR1) expression differ between chemosensitive and chemoresistant ovarian cancer?",

            # IMMUNE RESPONSE - Specific checkpoints
            "How does PD-L1 expression change after IFN-gamma exposure in melanoma cells?",

            # STEM CELLS - Specific markers
            "Does OCT4 expression differ between embryonic and induced pluripotent stem cells?",

            # APOPTOSIS - Specific pathways
            "How does caspase-8 activation differ between death receptor-mediated vs mitochondrial apoptosis?",

            # TRANSLATION - Specific factors
            "How does eIF2α phosphorylation alter global translation during ER stress?",

            # --- Dataset-aligned questions (one per VERIFIED GEO dataset) ---
            # These guarantee each dataset in the small verified pool is paired
            # with a biologically-matched question, so all of them are productive
            # instead of only the breast-cancer dataset. Without these the loop
            # re-runs one dataset repeatedly and the duplicate-statistical-profile
            # gate rejects the repeats (the observed ~90% rejection rate).
            # GSE13159 (leukemia, bone marrow vs peripheral blood)
            "How do gene expression profiles differ between bone marrow and peripheral blood leukemia samples?",
            "Which transcriptional programs distinguish acute myeloid leukemia in bone marrow from peripheral blood?",
            # GSE15822 (mouse liver, high-fat vs standard diet)
            "How does a high-fat diet alter hepatic gene expression compared to a standard diet in mouse liver?",
            "Which lipid-metabolism genes are differentially expressed in mouse liver under high-fat vs standard diet?",
            # GSE2034 (breast cancer relapse) — context-conditional variants so
            # re-runs probe different gene-set foci, reducing profile duplication.
            "Which cell-cycle and proliferation genes distinguish breast cancer bone relapse from no relapse?",
            "How do extracellular-matrix and adhesion pathways differ between relapsing and non-relapsing breast tumors?",
        ]

        logger.info(f"Generated {len(questions)} specific biological questions")
        return questions

    def generate_dataset_aligned_questions(self, datasets: List[Dict] = None) -> List[str]:
        """Return one biologically-matched question per verified dataset.

        Each verified dataset ships with a curated ``question`` describing its
        case/control design; pairing that question with its dataset guarantees a
        relevant match at the dataset-question gate. Use this to ensure every
        dataset in the (currently small) verified pool is exercised each cycle
        rather than burning cycles on question/dataset mismatches.
        """
        if datasets is None:
            try:
                from biodisc_core.fixed_pipeline.real_datasets import REAL_GEO_DATASETS
                datasets = REAL_GEO_DATASETS
            except Exception:  # noqa: BLE001
                datasets = []
        aligned = []
        for ds in datasets:
            q = ds.get("question")
            if q:
                aligned.append(q)
        return aligned

    def generate_context_conditional_questions(self) -> List[str]:
        """Module/pathway-focused questions that probe CONDITIONAL biology within
        each contrast (ASTRA §6/§7.5: push past the dominant pairwise signal toward
        context-specific relations). These are still answerable as case/control DE
        but frame the finding around a specific gene module — surfaced via the
        pathway-enrichment analysis, a step toward conditional biology. Full
        residual/subset analysis would realize them further.
        """
        return [
            # Breast cancer — module-focused
            "Which immune-response and inflammation genes distinguish breast cancer tumors from normal breast tissue?",
            "Which cell-cycle and proliferation genes are dysregulated in breast cancer vs normal?",
            # Mouse liver high-fat — module-focused
            "Which lipid-metabolism and fatty-acid pathway genes respond to a high-fat diet in mouse liver?",
            "Which insulin-signaling and glucose-metabolism genes change in mouse liver under high-fat vs standard diet?",
            # Pancreatic cancer — module-focused
            "Which extracellular-matrix and adhesion genes distinguish pancreatic tumors from normal pancreas?",
            # Lung adenocarcinoma — module-focused
            "Which DNA-repair and replication genes distinguish lung adenocarcinoma from normal lung?",
            "Which immune-checkpoint and antigen-presentation genes differ in lung adenocarcinoma vs normal?",
        ]

    def generate_question_pool(self, datasets: List[Dict] = None) -> List[str]:
        """Diverse + dataset-aligned + context-conditional pool, shuffled.

        Combining the broad specific-question list with dataset-aligned questions
        and module-focused context-conditional questions, then shuffling, varies
        which question is attempted first each cycle. This is the diversity lever
        that reduces duplicate-statistical-profile rejections (ASTRA §7.5) and
        primes toward non-obvious, conditional biology past the dominant signal.
        """
        pool = list(self.generate_specific_questions())
        pool.extend(self.generate_dataset_aligned_questions(datasets))
        pool.extend(self.generate_context_conditional_questions())
        # De-duplicate while preserving order, then shuffle for cycle variety.
        seen = set()
        unique = [q for q in pool if not (q in seen or seen.add(q))]
        random.shuffle(unique)
        return unique

    def get_question_context(self, question: str) -> Dict:
        """
        Provide context for a specific biological question.

        This helps with novelty assessment and interpretation.
        """
        contexts = {
            "BRCA1 mutation": {
                "field": "Cancer biology",
                "known_aspects": "BRCA1 role in DNA repair, synthetic lethality with PARP",
                "novel_angle": "Response heterogeneity in TNBC"
            },
            "STAT3 activation": {
                "field": "Signal transduction",
                "known_aspects": "STAT3 in inflammation and cancer",
                "novel_angle": "Glioblastoma-specific effects"
            },
            "AMPK activation": {
                "field": "Metabolism",
                "known_aspects": "AMPK as metabolic sensor",
                "novel_angle": "Glycolytic flux changes"
            },
        }

        # Simple keyword matching for context
        for keyword, context in contexts.items():
            if keyword in question:
                return context

        return {
            "field": "Biology",
            "novel_angle": "Specific biological mechanism",
            "testable": True
        }


def rank_datasets_for_question(question: str, datasets: List[Dict], mapper=None) -> List[tuple]:
    """Rank datasets by biological relevance to ``question`` (most relevant first).

    Returns a list of ``(relevance_score, dataset)`` sorted by score descending.
    Relevance = weighted overlap of organism / tissue / disease entities between
    the question and each dataset's title + curated question + organism, compared
    on canonical ontology IDs (so ``mouse`` matches ``mus musculus``,
    ``breast`` matches ``mammary``). Weights: organism 5, tissue 3, disease 2.

    This is the question<->dataset PINNING fix: a mouse-liver question is served
    the mus_musculus liver dataset first, a breast-cancer question the breast
    dataset, a leukemia question the bone-marrow/PB dataset. Previously every
    question was tried against a randomly-rotated dataset subset, producing
    incoherent pairings (e.g. a breast-cancer question run against a mouse
    high-fat-diet liver dataset) that nonetheless cleared the gates.
    """
    if mapper is None:
        from biodisc_core.fixed_pipeline.dataset_question_validation.ontology_mapper import OntologyMapper
        mapper = OntologyMapper()
    q = mapper.extract_entities(question)
    qo = mapper.normalize_organisms(q.get("organisms", set()))
    qt = mapper.normalize_tissues(q.get("tissues", set()))
    qd = mapper.normalize_diseases(q.get("diseases", set()))

    scored = []
    for idx, ds in enumerate(datasets):
        ds_text = f"{ds.get('title', '')} {ds.get('question', '')} {ds.get('organism', '')}"
        d = mapper.extract_entities(ds_text)
        do = mapper.normalize_organisms(d.get("organisms", set()))
        dt = mapper.normalize_tissues(d.get("tissues", set()))
        dd = mapper.normalize_diseases(d.get("diseases", set()))
        rel = 0
        if qo and do and (qo & do):
            rel += 5
        if qt and dt and (qt & dt):
            rel += 3
        if qd and dd and (qd & dd):
            rel += 2
        scored.append((rel, idx, ds))
    # sort by score desc, then original index for stable, deterministic ordering
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [(rel, ds) for (rel, _, ds) in scored]


def select_datasets_for_question(
    question: str, datasets: List[Dict], mapper=None, max_results: int = 3
) -> List[Dict]:
    """Return the biologically-matched datasets for ``question``, or ``[]`` if none.

    Pins a question to its most-relevant dataset(s) via
    :func:`rank_datasets_for_question`. If NO dataset shares any organism /
    tissue / disease entity with the question (best score 0), returns ``[]`` so
    the caller SKIPS the question instead of rotating it onto an unrelated
    dataset. Rotating an unmatched question onto a random dataset produces an
    incoherent candidate (e.g. a glioblastoma question on a breast-cancer
    dataset) that the entity-sparse validator cannot catch — and you cannot
    honestly answer a question with data that has no biological relation to it.
    """
    ranked = rank_datasets_for_question(question, datasets, mapper=mapper)
    # Return ONLY the datasets with a positive relevance score (capped at
    # max_results). Slicing ranked[:max_results] would pad with zero-score
    # (irrelevant) datasets when fewer than max_results match — defeating the
    # purpose. No positive match at all => [] (skip the question).
    matched = [ds for (score, ds) in ranked if score > 0]
    if not matched:
        return []
    return matched[:max_results]


def find_sibling_dataset(dataset_id: str, datasets: List[Dict], mapper=None) -> Optional[Dict]:
    """Return a sibling dataset (same tissue + disease, different id) for independent-
    cohort replication, or None. Two datasets are siblings when their titles map to
    a shared tissue AND disease entity (e.g. GSE2034 + GSE42568, both breast cancer).
    """
    if mapper is None:
        from biodisc_core.fixed_pipeline.dataset_question_validation.ontology_mapper import OntologyMapper
        mapper = OntologyMapper()

    def _ent(d):
        text = f"{d.get('title', '')} {d.get('question', '')} {d.get('organism', '')}"
        e = mapper.extract_entities(text)
        return (mapper.normalize_tissues(e.get("tissues", set())),
                mapper.normalize_diseases(e.get("diseases", set())))

    target = next((d for d in datasets if d.get("id") == dataset_id), None)
    if target is None:
        return None
    t_tis, t_dis = _ent(target)
    if not (t_tis and t_dis):
        return None
    for d in datasets:
        if d.get("id") == dataset_id:
            continue
        d_tis, d_dis = _ent(d)
        if d_tis and d_dis and (t_tis & d_tis) and (t_dis & d_dis):
            return d
    return None


def create_specific_questions_generator() -> SpecificQuestionsGenerator:
    """Factory function to create specific questions generator"""
    return SpecificQuestionsGenerator()
