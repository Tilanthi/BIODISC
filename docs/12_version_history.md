### Version Summary

**V8.0 - VERIFICATION-FIRST** (July 14, 2026):
- **Write chokepoint**: exactly ONE function (`discovery_store.append_verified`)
  may write a discovery, and it REQUIRES a machine `verification` block with
  objective real-data evidence. Fiction/hallucinated records are structurally
  impossible to store (ASTRA lesson #1).
- **Two stores**: `autonomous_discoveries.jsonl` = genuine (replicated) findings
  only; `autonomous_discoveries_candidates.jsonl` = machine-verified but
  unreplicated candidates (quarantined, never asserted as knowledge).
- **Real Gate-2** (`literature_gate.py`): PubMed abstract TF-similarity
  novelty check replaces the keyword heuristic; `known` claims are rejected,
  transient `retrieval_failed` is non-blocking and never cached.
- **Held-out replication anchor** (`replication_gate.py`): `is_genuine` requires
  the headline statistic to replicate on a held-out sample split.
- **Funnel instrumentation** (`verdict_log.py`): one structured verdict per
  candidate; `print_funnel()` shows where candidates die.
- **Single always-on path**: launchd → `discovery_watchdog.py` →
  `.fixed_autonomous_discovery.py`. Legacy V73 loops retired.
- **Evolution ON** (supervised, `evolution_integration.py`): AlphaEvolve-style
  method-evolution against benchmark ground truth; outputs are methods, not
  discoveries (separate provenance log). Real-cohort evaluator hook is the next step.
- **Question/dataset diversity** (2026-07-15): `specific_questions.py` now serves a
  diverse + dataset-aligned, shuffled question pool (`generate_question_pool`);
  `_search_real_geo_datasets` rotates the pool per cycle. This fixed a ~90%
  duplicate-statistical-profile rejection rate caused by re-running one question
  on one dataset. **Throughput is still capped by the 3-dataset verified pool**
  (GSE2034 / GSE13159 / GSE15822) — expanding it is the real next lever; the
  verdict funnel quantifies the rest.
- **Stability fixes** (2026-07-15, V8.0.2): (1) `geo_data_downloader` streamed
  matrix downloads are now hard-bounded by total wall-clock (10 min) + size
  (600 MB) via `_read_stream_bounded` — a stalled mid-stream read can no longer
  hang the loop for hours (the recurring stall). (2) Watchdog stall threshold
  lowered 6 h → 30 min (SIGTERM→SIGKILL escalation already present) so any
  residual hang is recovered promptly. (3) Organism normalization: the dataset-
  question validator now compares on canonical NCBITaxon IDs, so `mouse` matches
  `mus musculus` (was a false mismatch that rejected the entire GSE15822 mouse
  dataset). Same for tissue synonyms (`breast`↔`mammary`).
- **Question↔dataset pinning + skip-unmatched** (2026-07-15, V8.0.3):
  `_search_real_geo_datasets` serves each question only its biologically relevant
  datasets (`select_datasets_for_question` → `rank_datasets_for_question`: organism/
  tissue/disease entity overlap on canonical IDs). A mouse-liver question is pinned to
  the mus_musculus liver dataset, breast to the breast dataset, leukemia to bone-marrow/PB.
  **If no dataset is relevant (best score 0) the question is SKIPPED** (returns no
  datasets) — it is not rotated onto an unrelated dataset. This eliminates the incoherent
  pairings (e.g. a glioblastoma or breast-cancer question run against a mouse high-fat-diet
  liver dataset) that were clearing the entity-sparse validator and producing junk
  candidates. Tradeoff: lower raw throughput (questions with no matching data don't run),
  but every candidate produced is a coherent question↔dataset pairing.
- **RSI miner — a measured self-improvement loop** (2026-07-15, V8.0.4):
  `biodisc_core/fixed_pipeline/rsi_miner.py` (dependency-free, stdlib only) closes the
  loop the verdict log opened. It (1) MINES `discovery_verdicts.jsonl`, clustering
  rejections into failure themes (significance_failed, duplicate_profile,
  organism_mismatch, no_datasets, …) with per-day recurrence; (2) PROPOSES a concrete,
  **human-gated** fix per theme (`rsi_proposals.md` — propose-only, never auto-applies);
  (3) MEASURES whether an applied fix (recorded in `rsi_proposals_applied.jsonl`)
  actually reduced its failure class (before/after per-day recurrence → effectiveness
  0–100); (4) rolls up to `rsi_effectiveness.txt` — a number a capability index is
  designed to ingest *even when it lowers the headline*. Dogfooded live: the question↔dataset
  pinning fix scored 21.4/100 (duplicate rejections 10→4, "improving, not solved"). Run:
  `python -m biodisc_core.fixed_pipeline.rsi_miner`.
- **Verdict-logging coverage fix** (2026-07-15, V8.0.4b): `validate_discovery_comprehensive`
  now writes a PROVISIONAL verdict (`outcome=in_progress`, unique `vtok`) at the *start* of
  validation and the FINAL verdict (same `vtok`) at the end. `verdict_log.read_verdicts_dedup`
  collapses each pair to one record, and an orphaned provisional — a cycle killed
  mid-validation (watchdog SIGKILL) that never wrote its final — surfaces as a visible
  `abandoned_mid_validation` failure (its own funnel bucket + miner theme) instead of
  silently vanishing. This closes the blind spot where the miner undercounted exactly the
  failures it most needed to see. Verified live: 13 provisional+final pairs collapsed on
  the real log. (Coarse live-loop verdicts and legacy entries have no `vtok` and pass through.)
- **Replication bug fix — unblocks the genuine tier** (2026-07-15, V8.0.5): the
  held-out replication gate had been failing on *every* attempt (`np.where` "nonzero on
  0d" ValueError), so replication was always degraded → 0% replication → zero discoveries
  ever reached the genuine tier. Root cause: the gate passed group labels to the DE analyzer
  as a Python list, but the analyzer does `np.where(group_labels == 0)` which only compares
  element-wise on an ndarray. Fix: pass labels as an ndarray (plus a defensive `np.asarray`
  in the DE analyzer). Regression-tested with the *real* DE analyzer. The 18 quarantined
  candidates are now eligible for genuine-tier promotion once a candidate's top genes
  replicate on the held-out split.
- **Discovery-performance phases** (2026-07-15, V8.0.6–V8.0.9):
  - *1.5 replication criterion* — the gate now tests the top-N genes by p-value for
    direction+significance replication in the held-out split, instead of requiring
    FDR-significance in the (underpowered) discovery split (which dead-ended every candidate).
  - *Phase 2 metric isolation* — diagnosis showed the "significance-failure bottleneck" was
    **test pollution** (synthetic GSE11223/GSE99999 verdicts, zero on real datasets). `log_verdict`
    honors a `BIODISC_VERDICT_LOG` override; `tests/conftest.py` redirects test verdicts to tmp.
    The funnel/miner now read clean production data.
  - *Phase 4 capability index* — `capability_index.py`: a dated composite (replication_rate 0.5,
    gate_pass_rate 0.3, rsi_effectiveness 0.2) **designed to ingest inputs that lower its headline**.
    Today it reads **2.5/100** — honestly near-zero because replication (the load-bearing dimension)
    is 0. The watchdog runs the RSI miner + index hourly (the loop now turns on its own).
  - *Phase 3 dataset preflight + pool expansion* — `dataset_preflight.py` verifies a candidate GEO
    dataset through download → probe/gene mapping → binary design → differential signal; `--add`
    persists passing datasets to a `real_datasets_extra.json` sidecar (survives restart). **Pool
    expanded 3 → 6**: GSE42568 (breast, also an independent cohort for GSE2034), GSE15471 (pancreatic),
    GSE19188 (lung) — all GPL570 tumor-vs-normal, all passed preflight (362/1401/1226 sig genes).
- **Replication criterion = field-standard nominal-p bar** (2026-07-15, V8.0.11): the
  held-out replication gate now replicates a gene when it is **nominal p<0.05 + same
  direction** in the held-out split (previously required FDR<0.05 there). Requiring FDR
  in the *replication* cohort is non-standard and, with an underpowered 40% held-out
  split, blocked every promotion (live: 1/15 every time → 0% genuine). The accepted
  paradigm is discover-at-FDR, replicate-at-nominal-p; FDR correction belongs to
  discovery. `genuine`-tier records are stamped `method=internal_held_out_split_nominal_p`
  for auditability. This is the change that lets a coherent candidate actually reach
  the genuine tier.
- **🎯 FIRST GENUINE DISCOVERY** (2026-07-15, post-V8.0.11): `DISCOVERY_1784146695` —
  *"Which lipid-metabolism genes are differentially expressed in mouse liver under high-fat vs
  standard diet?"* (GSE15822). Cleared every gate: FDR-significant, real PubMed Gate-2 = "novel",
  and **internally replicated (10/15 top genes, fraction 0.67, nominal-p + same-direction on the
  held-out split)**. The first finding to reach the `genuine` tier — genuine-discovery yield moved
  from 0 → 1. (Internally replicated, not independently replicated; GSE42568 now enables the latter.)
- **Two discovery-quality levers** (2026-07-16, V8.0.13):
  - *Near-duplicate dedup (DE-gene overlap)* — the duplicate detector now rejects two discoveries
    on the same dataset that share ≥70% of their top DE genes (overlap coefficient), catching the
    same contrast re-derived under different question phrasings (the genuine store was inflating
    5× on the GSE15822 high-fat finding). Genuine count now reflects *distinct* findings.
  - *Independent-cohort replication* — when a candidate's dataset has a same-domain sibling in the
    pool (breast: GSE2034 + GSE42568), the discovery's top genes are replicated on the independent
    cohort (stronger than the internal held-out split). Genuine findings that clear it are stamped
    `method=independent_cohort`. The first lever past internal-only replication.
  - *Context-conditional question priming* — module/pathway-focused questions (immune, cell-cycle,
    lipid-metabolism, DNA-repair modules within each contrast) added to the pool, surfacing
    conditional biology via pathway enrichment (ASTRA §6/§7.5: push past the dominant pairwise signal).
- **Bug fixes for the two discovery levers** (2026-07-16, V8.0.14):
  - *Independent-cohort 0/0 fixed*: the cohort was downloaded with a 2000-gene subset that didn't
    cover the discovery's top genes + a gene-symbol case mismatch; now downloads 8000 genes (covers
    the discovery's set) and normalizes symbols (uppercase) before matching.
  - *Dedup persistence*: the near-duplicate gene-overlap registry is now persisted to
    `duplicate_registry.json` (env-overridable via `BIODISC_DUPLICATE_REGISTRY`), so cross-restart
    rediscoveries are caught. Test runs isolated via conftest (like the verdict log).
- Full test suite green (215 tests). See `docs/peer_review_fixes_implementation.md`.
- **Code-integrity audit** (2026-07-17, V8.0.16):
  - *Bypass-write neutralization* — the 4 dormant legacy direct-writes to the genuine store
    (`biodisc_v5_6_anti_stall_discovery.py`, `biodisc_v6_0_complete.py`,
    `biodisc_v6_0_fixed_integrated.py`, `biodisc_core/reasoning/v73_autonomous_discovery_working.py`)
    were replaced with `raise RuntimeError` (placed outside any swallowing `except`). The
    chokepoint is now structurally — not just conventionally — the only write path.
  - *Import-cascade fix* — `domains/__init__.py` no longer hard-imports the absent astrophysics
    modules `ism`/`star_formation` (ASTRA leftovers); they now degrade to `None` like the other
    optional domains, eliminating the "Domain system not available" warning cascade.
  - *Genuine-store hygiene* — ~6,200 legacy `is_genuine=None` rows removed from the active store
    (full pre-migration state preserved in git history; local archive + backup retained); the
    genuine store now holds only the 20 genuine + 6 rejected findings.
  - *Cosmetic* — `5-LAYER` → `6-LAYER` in orchestrator logs/docstrings (the code runs 6 gates);
    dead `output_file` param on `save_discovery` and dead `self.discoveries_file` removed.
    731-file syntax sweep = 34 broken files, exact `BROKEN_FILES_BASELINE.md` match, zero
    regressions. 215/215 tests pass.
- **Near-duplicate dedup fixed** (2026-07-17, V8.0.17): the V8.0.13 same-dataset
  gene-overlap dedup had never fired. Two compounding bugs: (1) the fingerprint read
  `dataset_id` only from the top level, but genuine reports store it under `dataset.geo_id`
  -> it came back empty -> the overlap check (keyed on dataset_id) was skipped and
  `duplicate_registry.json` was never persisted; (2) a fresh start had zero history. Fix:
  fingerprint falls back to `dataset.geo_id`/`gse_id`, and `DiscoveryCache` seeds
  `dataset_gene_sets` from the genuine store at init (production only; tests stay isolated
  via the existing conftest guard). Verified: a new question with >=70% top-gene overlap on
  a seeded dataset is now flagged as a near-duplicate. 215/215 tests pass.
- **no_datasets pre-filter** (2026-07-17, V8.0.18): ~33% of verdicts were `no_datasets`
  (the #1 funnel bucket) because the loop iterated the full mixed question pool every
  cycle and every broad-mechanistic question with no home in the 6-dataset verified pool
  logged a rejection. Added a question-validity pre-filter (`_filter_answerable_questions`)
  that drops questions with no matching verified dataset *before* iterating — a validity
  screen, not an interestingness screen (zero eureka cost). Uses the same matcher as the
  dataset search, so it never drops a question the loop would have accepted. Cuts ~15/37
  questions per cycle. 215/215 tests pass.
- **OntologyMapper synonyms** (2026-07-17, V8.0.19): the matcher had false negatives —
  e.g. an "hepatic" question failed to pin the liver dataset (GSE15822) because adjective
  forms weren't in the tissue map. Added collision-safe anatomical synonyms (hepatic->liver,
  cardiac->heart, pulmonary->lung, intestinal->colon, cutaneous->skin,
  neural/neuronal/cerebral->brain, pancreas/pancreatic) mapping to the same UBERON so
  `normalize_tissues` makes them compare equal. 'renal' omitted (substring of 'adrenal').
  Answerable-question rate 59%->62%. 215/215 tests pass.
- **Verified dataset pool expanded 6 -> 11** (2026-07-17, V8.0.20): ran `dataset_preflight` on
  diverse-tissue human GEO candidates; the five that cleared download -> binary case/control
  design -> probe/gene-symbol mapping -> differential signal were appended to
  `real_datasets_extra.json` (the sidecar the loop reads at import). New tissues — prostate
  (GSE6956, 89 samples), colorectal (GSE66360, 99; GSE4107, 22), kidney (GSE40435, 202),
  ovary (GSE14407, 24). Candidates that failed DOWNLOAD (not design/signal) were correctly
  rejected (GSE7696, GSE42861, GSE16011 — series-matrix formats the downloader can't parse).
  Each new tissue creates more question homes; answerable-question rate 62% -> 65%. Pool
  expansion is the structural throughput lever now that dedup is functional. 215/215 tests pass.
- **Eureka-steering rebuild** (2026-07-18, V8.0.21–25): the selector optimized for
  realness (replicability), which is anti-correlated with novelty — it surfaced
  textbook biology by construction (the most replicable signals on a public dataset
  are the ones already published). The rebuild holds realness as a floor and steers
  compute at surprise. (V8.0.21) value-of-compute gate: scores each question on
  novelty (1 - Gate-2 PubMed similarity), importance (hub-gene/pathway proxy),
  surprise (contrarian/reversal heuristic), cost (~log2 samples); funds top-k by EV
  + a 15% exploration slice before any DE — never silently drops the tail. (V8.0.22)
  contrarian/anti-textbook question generation — scores ~12x higher EV than
  confirmatory questions. (V8.0.23) cross-dataset module synthesis: finds genes that
  FLIP direction across datasets (a cross-context bridge) and shared modules;
  produces bridge hypotheses for review (not auto-stamped). anomaly_vs_expectation
  scaffolded (textbook-baseline is a research item, not faked). (V8.0.24) sandboxed
  hypothesis-as-code: 3-layer executor (process isolation + rlimits + timeout/temp
  cwd) around exec() of LLM code, opt-in via BIODISC_EVOLUTION_SANDBOX, OFF by
  default; run_method_evolution gated on the same flag. Also fixes a latent
  flaky-test root cause (Affymetrix _at probes now rejected locally, not via the
  HGNC network). (V8.0.25) under-studied-context pool expansion 11->13
  (GSE6764 liver-disease spectrum, GSE15653 biliary). 233 tests pass.
- **Eureka-steering rebuild: the analyzer half + metric** (2026-07-20, V8.0.26–30):
  the selector funded surprise-seeking questions but the analyzer still returned a
  generic top-DE signature, so contrarian findings could be stamped 'genuine' with
  an unrelated result (MTOR/MYC absent from their own findings) — selector and
  analyzer were mismatched. (V8.0.26) Layer-7 question-result binding gate rejects
  findings whose named gene isn't in the result; + organism-conflict exclusion in
  the dataset ranker (a mouse question no longer pairs with a human dataset — the
  relevance-gate sparse-metadata loophole). (V8.0.27) gene-specific hypothesis
  primitive: tests the NAMED gene's direction + significance directly, not a top-N
  list; Layer-7b rejects a FAILED contrarian (textbook held). (V8.0.28) cross-dataset
  direction primitive (queryable bridges). (V8.0.29) Gate-2 assesses the specific
  directional RESULT claim, not the question text. (V8.0.30) contrarian_success_rate
  metric (supported-and-novel) added to the capability index — the trend to watch.
  Suite green (240+ tests).

**V7.3 - PEER REVIEW FIXES** (July 10, 2026):
- 5-layer validation system to prevent pseudo-science
- Duplicate detection, dataset-question validation, probe-gene mapping
- FDR significance gates, template pattern detection
- **See**: `docs/peer_review_fixes_implementation.md`

**V7.2 - AUTO-RESTART & CONTROL PROBE FIXES** (July 10, 2026):
- Control probe filtering expanded (15+ patterns)
- Auto-restart system with watchdog monitoring
- Sleep/wake detection and crash recovery
- **See**: `docs/02_autonomous_system.md`

**V7.1 - MULTI-REPOSITORY EXPANSION** (July 7, 2026):
- Expanded from GEO-only to 13+ biological data repositories
- ~100+ million datasets (10-20x increase from GEO-only)
- Proteomics, metabolomics, epigenomics, clinical data, networks
- **See**: `docs/10_genuine_discovery_system.md`

**V7.0 - SCIENTIFIC INTEGRITY FIXES** (July 7, 2026):
- Gene symbol validation as HARD GATE
- Dataset verification with REAL accession numbers
- Real GEO data download implemented
- Fixed pipeline replacement (no more pseudo-science)
- **See**: `docs/10_genuine_discovery_system.md`

**V6.0 - CLOSED-LOOP DISCOVERY ARCHITECTURE** (July 4, 2026):
- 8 major architectural enhancements based on cutting-edge AI research
- Graded autonomy, epistemic collapse prevention
- Hybrid discovery engine with multi-paradigm reasoning
- **See**: `docs/04_architecture.md`

**V5.0 - GENUINE DISCOVERY SYSTEM** (July 1, 2026):
- Real literature validation via PubMed/NCBI
- Genuine database access (GEO, STRING, KEGG)
- Statistical validation with proper methodology
- **See**: `docs/10_genuine_discovery_system.md`
