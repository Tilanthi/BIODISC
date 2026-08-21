# RSI proposals — mined from discovery_verdicts.jsonl

_Candidate failures analyzed: 46652  (themes: 10)_
_Verdict coverage: 46570 rejected of 46595 logged (100%) — a system that stops logging failures would look healthier here for worse behavior._

_Propose-only. Applying any [APPROVAL] fix is a human-gated act; record it in rsi_proposals_applied.jsonl so its effect can be measured._

## 1. unclassified  [APPROVAL]
- occurrences: **43190**  (1257.45/day over 34.347d)
- proposed fix: Investigate root cause.
- samples:
    - Does TP53 change in the OPPOSITE direction in cancer than the textbook
    - Is the established relationship between PPARG and liver reversed in th
    - Does TP53 change in the OPPOSITE direction in leukemia than the textbo

## 2. generation_failed  [APPROVAL]
- occurrences: **1811**  (48.0/day over 37.729d)
- proposed fix: Root-cause the pre-validation failure (download timeout, gene-symbol validation, DE setup); treat as a reliability fix.
- samples:
    - Which lipid-metabolism genes are differentially expressed in mouse liv
    - Which lipid-metabolism genes are differentially expressed in mouse liv
    - How does eIF2α phosphorylation alter global translation during ER stre

## 3. duplicate_profile  [APPROVAL]
- occurrences: **871**  (22.997/day over 37.874d)
- proposed fix: Broaden question/dataset diversity or perturb DE so repeated pairs yield distinct statistical profiles (the small dataset pool is the deeper cause).
- samples:
    - How does novel gene X affect pathway Y in cancer?
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n
    - How does novel gene X affect pathway Y in cancer?

## 4. abandoned_mid_validation  [APPROVAL]
- occurrences: **356**  (9.85/day over 36.141d)
- proposed fix: Reliability: a validation cycle started but never wrote a final verdict — the process was likely killed mid-validation. Reduce mid-cycle kills (bound downloads, lengthen watchdog patience, avoid SIGKILL mid-cycle).
- samples:
    - How does DNA methylation at the MLH1 promoter differ between MSI-H and
    - How does BRCA1 mutation status affect response to PARP inhibitors in t
    - How do extracellular-matrix and adhesion pathways differ between relap

## 5. no_datasets  [auto-elig]
- occurrences: **228**  (103.846/day over 2.196d)
- proposed fix: Add a verified dataset matching this question's biology, or expand the ontology maps so the question finds a match.
- samples:
    - What is the relationship between p21 levels and G1/S checkpoint activa
    - How does MYOD expression fluctuate during myoblast differentiation vs 
    - Does VEGFA expression differ between hypoxic and normoxic conditions i

## 6. significance_failed  [APPROVAL]
- occurrences: **125**  (4.527/day over 27.61d)
- proposed fix: Review DE parameters (effect-size floor, FDR threshold, min-read filter); many matched question/dataset pairs still yield too few significant genes.
- samples:
    - Test question
    - Test question
    - How does BRCA1 mutation affect response to PARP inhibitors?

## 7. probe_gene_failed  [APPROVAL]
- occurrences: **24**  (26.639/day over 0.901d)
- proposed fix: Improve GPL probe->gene mapping coverage for the dataset's platform.
- samples:
    - Test question
    - Test question
    - Test question

## 8. tissue_mismatch  [APPROVAL]
- occurrences: **17**  (0.46/day over 36.988d)
- proposed fix: Expand the tissue ontology map, or add a dataset matching this tissue.
- samples:
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n

## 9. dataset_question_mismatch  [APPROVAL]
- occurrences: **17**  (0.46/day over 36.988d)
- proposed fix: Tighten question<->dataset pinning, or add the matching dataset.
- samples:
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n
    - How does BRCA1 mutation affect response to PARP inhibitors in triple-n

## 10. literature_known  [auto-elig]
- occurrences: **13**  (14.432/day over 0.901d)
- proposed fix: Reframe the question toward a less-established, more context-conditional angle.
- samples:
    - How does BRCA1 mutation status affect response to PARP inhibitors in t
    - How does BRCA1 mutation status affect response to PARP inhibitors in t
    - How does BRCA1 mutation status affect response to PARP inhibitors in t
