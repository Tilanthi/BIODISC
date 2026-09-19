# Paper2Agent-Inspired Verification Upgrades — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import Paper2Agent's verification discipline into BIODISC — real-data known-answer controls, a calibration registry + Gate-2 truth set, verifier-independence hardening, a limitations status taxonomy, and a method-acquisition admission route.

**Architecture:** Five independent upgrades to `biodisc_core/fixed_pipeline/`, all offline-testable, none touching the write chokepoint's single-path guarantee. Each follows existing patterns: Apache-2.0 header, factory functions, dataclasses, JSON artifacts at repo root, stdlib-only where the neighbors are stdlib-only.

**Tech Stack:** Python 3 (stdlib + numpy where already used), pytest. No new dependencies.

**Spec:** Session 2026-09-19 — the five recommendations from the Paper2Agent (Nature s41586-026-11044-y) analysis, approved by the user with "make all the upgrades you recommend."

## Global Constraints

- Apache-2.0 header (exact text as in `discovery_store.py:1-13`) on every new `.py` file.
- Factory functions, never direct constructors (project rule).
- **Never** add a second write path to the discovery store; `discovery_store.append_verified` stays the only chokepoint.
- All tests run offline (no network) except tests explicitly gated on env `BIODISC_GATE2_LIVE=1`.
- Version bump: **V9.1** (current is V9.0k per git log). Commit format `🧬 BIODISC: …`, push to `biodisc main` only.
- Verified interfaces (confirmed in-session):
  - DE analyzer: `create_differential_expression_analyzer().perform_differential_expression_analysis(expression_data: np.ndarray, gene_symbols: List[str], group_labels: np.ndarray, question: str, dataset_id: str) -> DifferentialExpressionAnalysis` with `.results` items exposing `.gene_symbol, .significant, .p_value, .fdr_p_value, .log2_fold_change`.
  - Orchestrator: `create_fixed_discovery_orchestrator().download_real_data_multi_repo(dataset_id=…, repository='GEO', n_samples=…, n_genes=…) -> (expression_data, gene_symbols, group_labels)`.
  - Genuine store: `autonomous_discoveries.jsonl` — 32 records; each has `discovery_id, question, dataset.geo_id, differential_expression.top_upregulated/top_downregulated (gene_symbol, log2_fold_change, fdr_p_value, regulation), replication.{replicated, method, replication_fraction}`.
  - Gate-2: `LiteratureNoveltyGate.assess(claim_text, question=None, fetcher=None) -> LiteratureVerdict(status ∈ novel|known|retrieval_failed, max_similarity, …)`; ctor default `similarity_threshold=0.55`; `fetcher: Callable[[query], List[(pmid, text)]]`.

---

### Task 1: Calibration registry (every invented constant carries provenance + staleness fingerprint)

**Files:**
- Create: `biodisc_core/fixed_pipeline/calibration_registry.py`
- Create: `calibration_registry.json` (repo root, next to `capability_index.json`)
- Test: `tests/test_calibration_registry.py`

**Interfaces:**
- Produces: `load_registry(path=None) -> dict`, `validate_against_code(registry) -> List[dict]` (`{id, registered, actual, ok}`), `staleness(registry, store_lines=None) -> List[dict]` (`{id, at_calibration, now, stale}`), `run(write=True) -> dict`, `main(argv=None) -> int`. Writes `calibration_report.json`.

Registry entries (exact current code values — verified this session):
```
anomaly_miner.EXTREME_LOG2FC = 1.0            (module attr)
replication_gate.NOMINAL_P = 0.05              (module attr)
capability_index.W_REPLICATION = 0.5           (module attr)
capability_index.W_GATE_PASS = 0.3             (module attr)
capability_index.W_RSI = 0.2                   (module attr)
LiteratureNoveltyGate ctor default similarity_threshold = 0.55   (ctor_default)
ReplicationGate ctor default min_fraction = 0.40                 (ctor_default)
ReplicationGate ctor default top_n = 15                          (ctor_default)
ReplicationGate ctor default min_replicated = 3                  (ctor_default)
fund_candidates default exploration_frac = 0.15                  (fn_default)
```
Entry shape: `{"id", "module", "kind" ("module_attr"|"ctor_default"|"fn_default"), "symbol", "params" (for ctor/fn: {"class"|"fn", "param"}), "value", "provenance": {"note", "calibrated_on", "store_lines_at_calibration"}, "stale_at_multiplier": 2.0}`. `store_lines_at_calibration` = genuine+candidate store line count at registration time (seed with 104: 32+72, counted this session).

Provenance notes (write these, they are the point):
- `EXTREME_LOG2FC`: "pool effect distribution: ~11% of reported genes reach 1.0 vs ~4% at 1.5 (V8.0.40, lowered from 1.5 to raise fire-rate)"
- `similarity_threshold`: "engineering judgment at V8.0 — NOT yet calibrated on a labeled truth set; see gate2_calibration.py (Task 2) which measures it"
- `exploration_frac`: "eureka-insurance slice (V8.0.21)"
- `NOMINAL_P`: "field-standard replication bar: discover at FDR, replicate at nominal p (V8.0.5)"
- `W_*`: "replication is the discovery criterion, so it carries the heaviest weight"

Implementation core:
```python
def _resolve_actual(entry):
    mod = importlib.import_module(f"biodisc_core.fixed_pipeline.{entry['module']}")
    if entry["kind"] == "module_attr":
        return getattr(mod, entry["symbol"])
    if entry["kind"] == "ctor_default":
        cls = getattr(mod, entry["params"]["class"])
        return inspect.signature(cls.__init__).parameters[entry["params"]["param"]].default
    fn = getattr(mod, entry["params"]["fn"])
    return inspect.signature(fn).parameters[entry["params"]["param"]].default

def staleness(registry, store_lines=None):
    store_lines = store_lines if store_lines is not None else _count_store_lines()
    out = []
    for e in registry["constants"]:
        at = e["provenance"].get("store_lines_at_calibration") or 0
        m = e.get("stale_at_multiplier", 2.0)
        out.append({"id": e["id"], "at_calibration": at, "now": store_lines,
                    "stale": store_lines >= m * max(at, 1)})
    return out
```

- [x] **Step 1: Write failing tests** — `test_registry_validates_against_live_code` (all entries `ok=True`), `test_tamper_detected` (monkeypatch `anomaly_miner.EXTREME_LOG2FC = 1.5` → that entry `ok=False`), `test_staleness_doubles` (at=104, now=208 → stale; now=207 → not stale), `test_run_writes_report` (tmp path, report JSON exists with `mismatches: []`).
- [x] **Step 2: Run** `pytest tests/test_calibration_registry.py -v` → FAIL (module missing).
- [x] **Step 3: Implement** `calibration_registry.py` + `calibration_registry.json`.
- [x] **Step 4: Run** → PASS.
- [x] **Step 5: Commit** `🧬 BIODISC: V9.1 calibration registry — provenance + staleness fingerprints for every pipeline constant`.

### Task 2: Gate-2 truth set + calibration (measure the gate that guards novelty)

**Files:**
- Create: `biodisc_core/fixed_pipeline/gate2_calibration.py`
- Create: `gate2_truth_set.json` (repo root) — `{"known_claims": [{"claim", "basis"}…], "novel_source": "genuine_store_questions"}`
- Test: `tests/test_gate2_calibration.py`

**Interfaces:**
- Consumes: `LiteratureNoveltyGate.assess(claim, fetcher=…)` (Task global constraints).
- Produces: `load_truth_set(path=None) -> dict`, `derive_novel_claims(store_path=None, cap=12) -> List[str]` (genuine-store `question` fields, most recent first), `evaluate(gate, known_claims, novel_claims) -> dict` with `{"known_accuracy", "novel_accuracy", "n_known", "n_novel", "per_claim": [{claim, expected, got, max_similarity}], "retrieval_failures": n}`, `run(live=False, write=True) -> dict` (offline: `fetcher`-injected self-check only; live: real PubMed), `main(argv) -> int` with `--live` flag. Writes `gate2_calibration_report.json`.

Author 24 known_claims (real, checkable textbook biology — shaped like pipeline claims, gene + condition + direction):
```
"BCL2 is upregulated in follicular lymphoma", "ERBB2 is overexpressed in HER2-positive breast cancer",
"TP53 is the most frequently mutated gene in human cancer", "MYC is amplified in Burkitt lymphoma",
"KRAS mutations are common in pancreatic cancer", "APC loss initiates colorectal tumorigenesis",
"PTEN loss activates PI3K AKT signaling", "VEGFA promotes tumor angiogenesis",
"SOD1 mutations cause familial ALS", "HBB mutation causes sickle cell anemia",
"CFTR mutations cause cystic fibrosis", "HFE mutations cause hereditary hemochromatosis",
"LDLR mutations cause familial hypercholesterolemia", "BRCA1 mutations increase breast cancer risk",
"CDKN2A deletion is common in melanoma", "BRAF V600E mutation is common in melanoma",
"IDH1 mutations occur in glioma", "JAK2 V617F mutation is common in polycythemia vera",
"BCR-ABL1 fusion drives chronic myeloid leukemia", "NOTCH1 mutations occur in T-cell acute lymphoblastic leukemia",
"EZH2 is overexpressed in many cancers", "TERT promoter mutations are common in melanoma",
"SMAD4 loss occurs in pancreatic cancer", "RB1 loss drives retinoblastoma"
```
each with `"basis": "textbook/established — must be scored known by Gate-2"`.

Docstring honesty note (required): the known side is external ground truth (catches an over-permissive gate letting textbook through); the novel side is seeded from the genuine store (regression — catches threshold drift that would kill real findings), because authoring "novel" claims by hand would be guessing.

- [x] **Step 1: Write failing tests (offline, injected fetchers/fakes)** — `test_evaluate_scoring_math` (FakeGate returns known for all known_claims, novel for all novel_claims → accuracies 1.0), `test_evaluate_counts_errors` (one wrong per side → 0.75/… per counts), `test_entailing_abstract_scores_known` (real `LiteratureNoveltyGate` with `fetcher` returning `("1", "TP53 is the most frequently mutated gene in human cancers and its loss …")` → that claim `known`), `test_unrelated_abstract_scores_novel` (fetcher returns abstract about photosynthesis → `novel`), `test_derive_novel_claims_reads_store` (tmp jsonl with 2 genuine records → 2 claims, candidates excluded), `test_retrieval_failures_not_counted` (FakeGate returns retrieval_failed → excluded from accuracy denominators, counted in `retrieval_failures`). Live test `test_live_calibration` with `@pytest.mark.skipif(not os.environ.get("BIODISC_GATE2_LIVE"), …)`.
- [x] **Step 2: Run** → FAIL.
- [x] **Step 3: Implement** module + truth set JSON.
- [x] **Step 4: Run** → PASS.
- [x] **Step 5: Commit** `🧬 BIODISC: V9.1 Gate-2 truth set + calibration — the novelty gate is now itself measured`.

### Task 3: Real-data known-answer control suite (the pipeline must recover what it verified)

**Files:**
- Create: `biodisc_core/fixed_pipeline/known_answer_controls/__init__.py` (exports + docstring)
- Create: `biodisc_core/fixed_pipeline/known_answer_controls/cases.py`
- Create: `biodisc_core/fixed_pipeline/known_answer_controls/runner.py`
- Create: `known_answer_cases.json` (repo root — generated by the seed CLI, not hand-written)
- Modify: `biodisc_core/fixed_pipeline/capability_index.py` (ingest the report; no formula change)
- Test: `tests/test_known_answer_controls.py`

**Interfaces:**
- Produces (cases.py): `KnownAnswerCase` dataclass `{case_id, dataset_id, question, genes: [{symbol, direction, log2fc, fdr}], source="genuine_store", discovery_id, seeded_at}`, `seed_from_genuine_store(store_path=None, max_cases=10) -> List[KnownAnswerCase]` (most-recent replicated genuine records; up to 5 top genes each by |log2FC|), `save_cases(cases, path)`, `load_cases(path)`.
- Produces (runner.py): statuses `PASS | FAIL_DIRECTION | FAIL_SIGNIFICANCE | FAIL_ABSENT | SKIP_NO_DATA | ERROR` (Paper2Agent-style labeled ladder, never silently green); `run_controls(cases=None, data_resolver=None, analyzer=None, min_gene_recovery=0.7) -> dict` report `{ran_at, n_cases, summary: {pass, fail, skip, error}, pass_rate, results: [{case_id, dataset_id, status, genes: [{symbol, expected_direction, observed_direction, observed_fdr, ok}], reason}]}`; default `data_resolver` = lazy orchestrator `download_real_data_multi_repo` wrapped in try/except → `SKIP_NO_DATA`; default analyzer = real `create_differential_expression_analyzer()`; gene verdict: absent → `FAIL_ABSENT`, sign mismatch → `FAIL_DIRECTION`, `fdr >= 0.05` → `FAIL_SIGNIFICANCE`, else ok; case PASS iff `ok_fraction >= min_gene_recovery`; `main(argv)` CLI with `--seed` and `--max-cases N`.
- capability_index: `compute_capability_index(...)` output gains `"known_answer_controls": {pass_rate, n_pass, n_fail, n_skip, ran_at} | None` read from `known_answer_report.json` if present.

Per-gene check core:
```python
def _gene_verdict(exp, by_gene):
    r = by_gene.get(exp["symbol"].upper())
    if r is None:
        return "FAIL_ABSENT", None, None
    obs_dir = "up" if r.log2_fold_change >= 0 else "down"
    fdr = getattr(r, "fdr_p_value", None)
    if obs_dir != exp["direction"]:
        return "FAIL_DIRECTION", obs_dir, fdr
    if fdr is None or fdr >= 0.05:
        return "FAIL_SIGNIFICANCE", obs_dir, fdr
    return "ok", obs_dir, fdr
```

- [x] **Step 1: Write failing tests** — `test_seed_from_genuine_store` (tmp store with 2 records incl. 1 candidate → only genuine seeded, genes capped at 5), `test_run_controls_pass_on_recovering_data` (numpy: 40 genes × 16 samples, GENE_A mean +2 in group 1, GENE_B −2; real analyzer; case expecting A up / B down → PASS), `test_fail_direction_when_flipped` (expect A down → FAIL_DIRECTION), `test_skip_no_data_on_resolver_error` (resolver raises → SKIP_NO_DATA, not ERROR), `test_report_written_and_capability_index_ingests` (tmp report JSON; `compute_capability_index` with injected tmp `DATA_ROOT` or monkeypatched report path returns the block).
- [x] **Step 2: Run** → FAIL.
- [x] **Step 3: Implement** package + capability_index hook.
- [x] **Step 4: Run** → PASS. Then run `python -m biodisc_core.fixed_pipeline.known_answer_controls --seed` once to generate `known_answer_cases.json` from the 32 genuine records.
- [x] **Step 5: Commit** `🧬 BIODISC: V9.1 known-answer control suite — regression tripwire for real-data wiring (V8.0.34-class bugs become daily failures)`.

### Task 4: Verifier-independence hardening (kill the unconditional assertion in the verification block)

**Files:**
- Modify: `biodisc_core/fixed_pipeline/discovery_store.py:164-198` (`build_verification_block`)
- Create: `docs/13_verifier_independence_audit.md`
- Test: extend `tests/test_discovery_chokepoint.py`

**Interfaces:**
- Bug being fixed: `build_verification_block` hardcodes `"fdr_significance": True` — an unconditional assertion in the machine evidence block (Paper2Agent rule violated: "worker completion alone does not establish success").
- Produces: `fdr_significance` derived from the report's recorded stats — `report['comprehensive_validation_statistics']['fdr_significance_gate']['passes_significance_gate']`; fall back to `report['validation_statistics']` same path; `None` (unknown) when neither present — never asserted True without evidence.

```python
def _fdr_passed(report: dict):
    for stats_key in ("comprehensive_validation_statistics", "validation_statistics"):
        stats = report.get(stats_key) or {}
        g = stats.get("fdr_significance_gate") or {}
        v = g.get("passes_significance_gate")
        if v is not None:
            return bool(v)
    return None   # unknown — recorded as unknown, never asserted
```

Audit doc: table over Layers 1–7 + replication + chokepoint — "re-derives from primary data" vs "consumes producer output" (replication gate re-runs DE on both splits itself → independent; independent-cohort gate recomputes cohort DE → independent; Gate-2 sees only claim text → independent; the one defect found was the hardcoded FDR flag — fixed here; the doc records the method and the Paper2Agent provenance of the rule).

- [x] **Step 1: Write failing tests** — `test_verification_block_reflects_actual_fdr_failure` (report with stats `passes_significance_gate: False` → block records `False`), `test_verification_block_reflects_fdr_pass`, `test_verification_block_unknown_when_stats_absent` (no stats → `None`).
- [x] **Step 2: Run** → FAIL (current code returns True always).
- [x] **Step 3: Implement** the derivation in `discovery_store.py`; write the audit doc.
- [x] **Step 4: Run full chokepoint tests** → PASS.
- [x] **Step 5: Commit** `🧬 BIODISC: V9.1 verifier-independence fix — verification block no longer asserts FDR passage unconditionally + layer audit doc`.

### Task 5: Limitations taxonomy (`verified_with_limitations` between genuine and candidate)

**Files:**
- Modify: `biodisc_core/fixed_pipeline/discovery_gate.py` (FlagDecision + evaluate_for_flagging + stamp_report)
- Modify: `biodisc_core/fixed_pipeline/capability_index.py` (report the breakdown; no formula change)
- Test: `tests/test_discovery_gate_limitations.py`

**Interfaces:**
- Produces: `FlagDecision(tier, is_genuine, reason, limitations: List[str], status: str)` where `status ∈ {"verified", "verified_with_limitations"}` (genuine tier only; candidates stay `candidate_unconfirmed`). `stamp_report` writes `flagging.status` + `flagging.limitations`. Readers must treat missing `status` as `verified` (backward compat with 32 existing records).
- Limitation detectors (machine-checkable, conservative — only for genuine tier):
```python
def _limitations_of(report: dict) -> List[str]:
    out = []
    rep = report.get("replication") or {}
    if rep.get("replicated"):
        if rep.get("method") == "internal_held_out_split_nominal_p":
            out.append("internal_replication_only")   # not independent-cohort
        try:
            if float(rep.get("replication_fraction", 1.0)) < 0.5:
                out.append("weak_replication_fraction")
        except (TypeError, ValueError):
            pass
    lit = (report.get("comprehensive_validation_statistics") or {}).get("literature_novelty") or {}
    sim = lit.get("max_similarity")
    if isinstance(sim, (int, float)) and sim >= 0.55 - 0.05:
        out.append("novelty_margin_thin")             # within 0.05 of the known threshold
    return out
```
- capability_index: `_count_store` gains limitation/status breakdown from genuine store — output `"verified_with_limitations": n, "limitation_breakdown": {reason: count}` under `drivers`.

- [x] **Step 1: Write failing tests** — `test_internal_replication_gets_limitation`, `test_independent_cohort_clean` (method `independent_cohort`, fraction 0.8, sim 0.10 → `status="verified"`, `limitations == []`), `test_thin_novelty_margin_flagged` (sim 0.52 → `novelty_margin_thin`), `test_weak_fraction_flagged` (0.4 → `weak_replication_fraction`), `test_backward_compat_missing_status` (capability-index counting treats absent `flagging.status` as `verified`).
- [x] **Step 2: Run** → FAIL.
- [x] **Step 3: Implement** both files.
- [x] **Step 4: Run** → PASS.
- [x] **Step 5: Commit** `🧬 BIODISC: V9.1 limitations taxonomy — genuine tier now carries machine-readable verification_with_limitations states`.

### Task 6: Method-acquisition admission route + RSI confinement policy

**Files:**
- Create: `biodisc_core/fixed_pipeline/method_acquisition/__init__.py`
- Create: `biodisc_core/fixed_pipeline/method_acquisition/admission.py`
- Create: `biodisc_core/fixed_pipeline/method_acquisition/policy.py`
- Create: `acquired_methods.json` (repo root, `{"methods": []}`)
- Modify: `biodisc_core/fixed_pipeline/rsi_miner.py` (tag each theme's route; no behavior change to mining)
- Test: `tests/test_method_acquisition.py`

**Interfaces:**
- admission.py: `AcquiredMethod` dataclass `{method_id, name, source_repo, source_commit, source_paper, tools, state ∈ quarantined|admitted|rejected, evidence: {reference_agreement: bool, store_fpr_check: bool, human_review: bool}}`; `ADMISSION_REQUIREMENTS = ["reference_agreement", "store_fpr_check", "human_review"]` (Paper2Agent: reference run before implementation; 74/100 conversion ⇒ quarantine until evidenced); `evaluate_admission(m) -> {"state", "unmet": [...]}` (admitted only when all evidence true; quarantined otherwise; rejected only by explicit human `reject` action); `load_registry/save_registry(path)`; `is_admitted(method_id, path) -> bool` — the single gate the pipeline must consult before any acquired method mints candidates.
- policy.py: `SCIENTIFIC_PATH_PATTERNS = ("differential_expression", "anomaly_miner", "gene_specific_hypothesis", "fdr_significance_gate", "replication_gate", "literature_gate", "value_of_compute", "pathway_analysis", "benchmark")`; `classify_path(path) -> "plumbing" | "scientific_algorithm"` (substring match on the fixed_pipeline-relative path); `classify_proposal(theme) -> {"change_class", "route"}` where route = `method_acquisition` for scientific, `rsi_direct` for plumbing; `THEME_CLASS` explicit map for all 13 rsi_miner themes (significance_failed→scientific_algorithm; probe_gene_failed→plumbing; organism/tissue/disease_mismatch→plumbing; duplicate_profile→plumbing; literature_known→plumbing; no_datasets→plumbing; generation_failed→plumbing; exception→plumbing; abandoned_mid_validation→plumbing; template_question→scientific_algorithm; dataset_question_mismatch→plumbing) with default `scientific_algorithm` (conservative: unknown changes route to acquisition, never silently auto-apply).
- rsi_miner.py: `Pattern` gains `change_class: str = ""` and `route: str = ""`; `mine()` fills them via `classify_proposal`; `write_proposals_md` prints `- route: {route} ({change_class})` per pattern — for scientific_algorithm themes the line reads `route: method_acquisition (scientific algorithm — must pass admission, never RSI-direct)`. Mining logic unchanged.
- Docstring cites the Paper2Agent rule: "Do not invent scientific algorithms to fill repository gaps" — RSI stays confined to plumbing; scientific methods enter only through acquisition-with-reference-agreement.

- [x] **Step 1: Write failing tests** — `test_admission_requires_all_evidence` (all-false → quarantined with 3 unmet; all-true → admitted; `is_admitted` false/true accordingly), `test_rejected_only_explicit`, `test_classify_paths` (each pattern → scientific; `FixedDiscoveryOrchestrator.py`, `verdict_log.py`, watchdog → plumbing), `test_theme_routes` (significance_failed → method_acquisition; organism_mismatch → rsi_direct; unknown theme → method_acquisition), `test_rsi_proposals_md_shows_routes` (mine a tmp verdict list, write md, assert both route strings appear).
- [x] **Step 2: Run** → FAIL.
- [x] **Step 3: Implement** package + rsi_miner tagging.
- [x] **Step 4: Run** `pytest tests/test_method_acquisition.py tests/test_rsi_miner.py -v` → PASS.
- [x] **Step 5: Commit** `🧬 BIODISC: V9.1 method-acquisition admission route — scientific algorithms enter only with reference agreement; RSI confined to plumbing`.

### Task 7: Docs, version bump, full suite, push

**Files:**
- Modify: `CLAUDE.md` (version line → V9.1 VERIFICATION HARDENING; add one Critical Reminders bullet)
- Modify: `docs/12_version_history.md` (V9.1 entry dated 2026-09-19 at the top of the current-version section, same format as V8.0.38 entry)
- Run: `python -m pytest tests/ -q` → all green (existing 245+ plus ~28 new)
- Run CLIs once each: `python -m biodisc_core.fixed_pipeline.calibration_registry`, `python -m biodisc_core.fixed_pipeline.gate2_calibration` (offline self-check), `python -m biodisc_core.fixed_pipeline.known_answer_controls --seed` (Task 3 does this); leave `--live`/full-data runs to the operator and say so.
- Commit `🧬 BIODISC: V9.1 verification hardening — Paper2Agent lessons (known-answer controls, calibration registry, Gate-2 truth set, verifier independence, limitations taxonomy, method-acquisition route)` and `git push biodisc main`.

---

## Self-Review

1. **Spec coverage:** all five session recommendations → Task 1+2 (rec #2 calibration registry + Gate-2 truth set), Task 3 (rec #1 known-answer controls), Task 4 (rec #3 verifier independence), Task 5 (rec #4 status taxonomy), Task 6 (rec #5 method acquisition + RSI confinement). ✓
2. **Placeholder scan:** every step carries exact constants, signatures, claim texts, or code; no TBD/“add appropriate X”. ✓
3. **Type consistency:** `KnownAnswerCase.genes[].direction` uses "up"/"down" (matches `regulation` values in the store); runner consumes `fdr_p_value` attribute (matches DE results objects); `classify_proposal` names match rsi_miner's 13 themes. ✓
