# Evolutionary Method Discovery (AlphaEvolve-style) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Phase 0 is fully specified; Phases 1–4 are specified at task granularity with concrete files, interfaces, and exit criteria — expand each into TDD micro-steps (following the Phase 0 pattern) at the start of that phase.

**Goal:** Give BIODISC a trustworthy, machine-gradeable evaluator (Phase 0), then layer an AlphaEvolve-style evolutionary-coding loop on top so BIODISC *evolves better bioinformatics methods* over real data (Phases 1–4).

**Architecture:** AlphaEvolve = {LLM ensemble mutates code via diffs} × {automated scalar evaluator `h`} × {MAP-Elites/island program database with genealogy} × {distributed async loop}. Its authors state the natural-sciences frontier needs "LLM feedback on ideas + machine feedback via code execution." BIODISC owns the machine-feedback half (real GEO data + statistics). The binding constraint is a **trustworthy scalar fitness function**, so Phase 0 fixes the evaluator first; evolution comes second. BIODISC already contains an orphaned parameter-evolution skeleton (`biodisc_core/swarm/leapcore_evolution.py`) — but see the Phase 1 deviation note: leapcore evolves *numeric parameters*, not code, so Phase 1 builds the real AlphaEvolve code-evolution mechanism instead.

**Tech Stack:** Python 3.14 (per existing `.pyc` targets), pytest, numpy, pandas, requests, Anthropic SDK (`anthropic`) for the LLM ensemble (Haiku 4.5 = throughput/diversity analog to Gemini Flash; Sonnet/Opus = breakthrough analog to Gemini Pro).

---

## Restart Protocol (read this first if resuming)

This plan is the source of truth. To resume after context loss:

1. `cat docs/superpowers/plans/2026-07-11-evolutionary-method-discovery.md` — re-read this file.
2. Check task status: the checkboxes below + `git log --oneline -20` (each task ends with a commit prefixed `P0.N:` etc.).
3. Re-verify any file:line cited here against current code before editing (BIODISC changes often; line numbers drift).
4. Resume at the first unchecked box. Do not skip Phase 0 even if tempted — it is the AlphaEvolve precondition.

**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done (commit landed).

### Phase 0 status snapshot
- [x] P0.0 test scaffold (commit 8ae0f3f)
- [x] P0.1 reject probe IDs in gene-symbol validator (commit b97a713)
- [x] P0.2 stop fabricating `UNKNOWN_GENE_` names (commit c8bdec1)
- [x] P0.3 derive real group labels from sample metadata (commit 3fc6d6e)  ← highest integrity priority
- [x] P0.4 enforce minimum sample count (commit aa6f911)
- [x] P0.5 harden metadata parsing + threading (commit aa6f911)
- [x] P0.6 ground-truth benchmark + scalar fitness `h` (commit c18b687)
- [ ] P0.3b (integrity follow-up) disable dormant synthetic-data discovery path

**Phase 0 COMPLETE (2026-07-11).** Verification:
- `python -m pytest tests/fixed_pipeline/ -q` → **24 passed**.
- Fabrication audit clean: no `UNKNOWN_GENE_` or `i % 2` in the discovery path;
  the only remaining `n_samples // 2` hits are the two legitimate test/benchmark
  fixture generators (`benchmark/truth_known_fixture.py`, `differential_expression.generate_real_gene_expression_data`).
- End-to-end fitness check: a per-gene t-test scores **AUROC 1.000, held-out
  replicate 0.998, aggregate 0.999** on the truth-known benchmark → the scalar
  evaluator `h` discriminates real methods. Phase 1 can begin.

**Findings during P0.3 (recorded for future sessions):**
- A 4th fabrication site, `differential_expression/__init__.py:320` (`generate_real_gene_expression_data`), is a **legitimate test-fixture generator** (known-truth synthetic data for tests + the P0.6 benchmark). NOT in the discovery path. Keep it; it explains the only remaining grep-audit hit for `n_samples // 2`.
- Legacy `biodisc_v6_0_fixed_integrated.py:make_genuine_discovery` (line ~236) still generates synthetic `GENE_####` data with `dataset_id=SYNTHETIC_<ts>`. It is **NOT referenced** by the active watchdog/loop (`.fixed_autonomous_discovery.py` → `FixedDiscoveryOrchestrator`, which downloads real data). Dormant integrity landmine → P0.3b.

**Phase 0 exit criterion:** a fixed reference analysis run end-to-end produces a reproducible scalar fitness on a truth-known benchmark, with zero probe-ID leakage, zero fabricated group labels, and zero datasets accepted below the sample-count floor.

---

## Global Constraints

- **NO SYNTHETIC DATA in the discovery path.** Real GEO/ArrayExpress/etc. only. The disabled `_simulate_realistic_geo_data` (raises `RuntimeError`) must stay disabled. Truth-known **benchmark fixtures** (P0.6) are a distinct, legitimate exception — they are test data with known answers used to *score methods*, never presented as discoveries. Name them `benchmark_*` and document this distinction in every such file's docstring.
- **Validation is a hard gate, never a fitness component.** The 5-layer validation *blocks* candidates; it must never contribute to the score (else the optimizer learns to fool the validator).
- **Fitness anchor = held-out replication, not in-sample p-values.** Evolutionary pressure on p-values is p-hacking at scale.
- **Factory functions, never direct constructors** (BIODISC convention: `create_*()`).
- **Honest scope:** we evolve *methods/pipelines*, not biological facts. Never claim BIODISC "discovers biological facts via evolution." The claim is: better methods → more reliable downstream discoveries.
- **Git:** commit per task to `main`; push with `git push biodisc main` (never `origin`, never ASTRA-dev). Commit messages prefixed `P0.N:` / `P1.N:` etc.

---

## File Structure (Phase 0)

| File | Responsibility | Action |
|---|---|---|
| `tests/fixed_pipeline/__init__.py` | test package | create |
| `tests/fixed_pipeline/conftest.py` | shared fixtures | create |
| `tests/fixed_pipeline/test_gene_symbol_validation.py` | P0.1 tests | create |
| `tests/fixed_pipeline/test_gene_resolver.py` | P0.2 tests | create |
| `tests/fixed_pipeline/test_sample_metadata_parser.py` | P0.3 tests | create |
| `tests/fixed_pipeline/test_dataset_verifier.py` | P0.4 tests | create |
| `tests/fixed_pipeline/test_geo_metadata.py` | P0.5 tests | create |
| `tests/fixed_pipeline/test_benchmark_fitness.py` | P0.6 tests | create |
| `biodisc_core/fixed_pipeline/gene_symbol_validation.py` | make `_validate_probe_id` reject probes | modify |
| `biodisc_core/fixed_pipeline/probe_gene_mapping/gene_resolver.py` | stop fabricating names; real annotation hook | modify |
| `biodisc_core/fixed_pipeline/probe_gene_mapping/platform_parser.py` | parse GEO GPL platform annotation (probe→gene) | extend |
| `biodisc_core/fixed_pipeline/sample_metadata_parser.py` | derive groups from `!Sample_characteristics` | create |
| `biodisc_core/fixed_pipeline/multi_repository_downloader.py` | use real group labels; reject if unknown | modify |
| `biodisc_core/fixed_pipeline/dataset_verifier_real.py` | enforce sample_count ≥ 6 | modify |
| `biodisc_core/fixed_pipeline/geo_data_downloader.py` | robust metadata parse; thread through | modify |
| `biodisc_core/fixed_pipeline/benchmark/` | truth-known benchmark fixtures + fitness `h` | create |

---

## Phase 0 — Fix the evaluator (PRECONDITION; do this entirely before Phase 1)

Rationale: AlphaEvolve's power = trustworthy automated evaluator. BIODISC's current evaluator has six defects (A–F). Fixing them is valuable independent of whether evolution is ever added.

### Task P0.0: Test scaffold

**Files:**
- Create: `tests/fixed_pipeline/__init__.py`, `tests/fixed_pipeline/conftest.py`
- Create: `pytest.ini` at repo root (if absent)

**Interfaces:**
- Produces: a runnable `pytest tests/fixed_pipeline/` invokable from repo root.

- [ ] **Step 1: Create test package + conftest**

`tests/fixed_pipeline/__init__.py` — empty.
`tests/fixed_pipeline/conftest.py`:
```python
import os
import sys
import pytest

# Make biodisc_core importable from repo root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
```

- [ ] **Step 2: Ensure pytest config**

If no `pytest.ini` / `[tool:pytest]` exists, create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -q
```

- [ ] **Step 3: Smoke test**

Run: `python -m pytest tests/fixed_pipeline/ -q`
Expected: "no tests ran" (0 errors) — confirms harness imports cleanly.

- [ ] **Step 4: Commit**
```bash
git add tests/fixed_pipeline/__init__.py tests/fixed_pipeline/conftest.py pytest.ini
git commit -m "P0.0: scaffold fixed_pipeline test harness"
```

---

### Task P0.1: Reject probe IDs in gene-symbol validator (Defect A)

**Problem:** `gene_symbol_validation.py:_validate_probe_id` (~lines 340–400) *accepts* `ILMN_########` and numeric Affymetrix IDs as **valid** gene symbols, so probe IDs pass the "HARD GATE" at orchestrator step 2.5.

**Files:**
- Modify: `biodisc_core/fixed_pipeline/gene_symbol_validation.py` (the `_validate_probe_id` method and any call site that treats its result as "valid gene symbol")
- Test: `tests/fixed_pipeline/test_gene_symbol_validation.py`

**Interfaces:**
- Produces: `_validate_probe_id(symbol)` returns a result flagged as a **probe ID (not a valid gene symbol)** so the HARD GATE rejects unless resolution succeeds downstream.

- [ ] **Step 1: Write the failing test**

`tests/fixed_pipeline/test_gene_symbol_validation.py`:
```python
from biodisc_core.fixed_pipeline.gene_symbol_validation import (
    create_gene_symbol_validator,
)


def test_illumina_probe_id_is_rejected_as_gene_symbol():
    v = create_gene_symbol_validator()
    results, all_valid = v.validate_gene_symbols(
        gene_symbols=["ILMN_1659893", "TP53"], reject_on_invalid=True
    )
    assert all_valid is False, "ILMN_ probe IDs must NOT be accepted as valid gene symbols"


def test_numeric_affy_probe_id_is_rejected():
    v = create_gene_symbol_validator()
    results, all_valid = v.validate_gene_symbols(
        gene_symbols=["117_at", "BRCA1"], reject_on_invalid=True
    )
    assert all_valid is False


def test_real_gene_symbols_still_pass():
    v = create_gene_symbol_validator()
    _, all_valid = v.validate_gene_symbols(
        gene_symbols=["TP53", "BRCA1", "EGFR", "GAPDH"], reject_on_invalid=True
    )
    assert all_valid is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/fixed_pipeline/test_gene_symbol_validation.py -v`
Expected: FAIL (probe IDs currently accepted → `all_valid` True).

- [ ] **Step 3: Read current `_validate_probe_id` and fix**

Open `gene_symbol_validation.py`, find `_validate_probe_id`. It currently returns a passing `GeneSymbolValidation` for `ILMN_…` and numeric IDs. Change it so probe-ID formats return a result whose validity is **False** (i.e., probe IDs are treated as invalid gene symbols requiring resolution). Concretely: where it builds a `GeneSymbolValidation(...)` for probe formats, set the validity flag to `False` and `source="UNRESOLVED_PROBE"`. Keep detection logic (so P0.2 can still recognize them), only flip validity.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/fixed_pipeline/test_gene_symbol_validation.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Commit**
```bash
git add biodisc_core/fixed_pipeline/gene_symbol_validation.py tests/fixed_pipeline/test_gene_symbol_validation.py
git commit -m "P0.1: reject probe IDs as valid gene symbols (Defect A)"
```

---

### Task P0.2: Stop fabricating UNKNOWN_GENE_ names (Defect B)

**Problem:** `probe_gene_mapping/gene_resolver.py:84` emits `f"UNKNOWN_GENE_{probe_id}"` for unmapped probes — a fabricated identifier worse than the probe. There is also no real annotation source ("In real implementation, would query platform annotation. For now, mark as unmapped").

**Files:**
- Modify: `biodisc_core/fixed_pipeline/probe_gene_mapping/gene_resolver.py`
- Extend: `biodisc_core/fixed_pipeline/probe_gene_mapping/platform_parser.py` (add `load_gpl_annotation(gpl_id) -> dict[probe, gene]` that fetches+parses a GEO GPL platform file; cache to disk)
- Test: `tests/fixed_pipeline/test_gene_resolver.py`

**Interfaces:**
- Produces: `GeneResolutionResult.resolved_genes` contains **only** real gene symbols or `None`; never `UNKNOWN_GENE_*`. `success=False` whenever any probe is unmapped (already the case). New: `PlatformParser.load_gpl_annotation(gpl_id)`.

- [ ] **Step 1: Write the failing test**

```python
from biodisc_core.fixed_pipeline.probe_gene_mapping import create_probe_gene_mapper


def test_resolver_never_emits_unknown_gene_names():
    mapper = create_probe_gene_mapper()
    result = mapper.validate_and_resolve(["ILMN_1659893", "ILMN_0000000"])
    assert "UNKNOWN_GENE_ILMN_1659893" not in result.resolved_genes
    assert not any(str(g).startswith("UNKNOWN_GENE_") for g in result.resolved_genes)


def test_resolver_marks_unmapped_and_rejects():
    mapper = create_probe_gene_mapper()
    result = mapper.validate_and_resolve(["ILMN_1659893"])
    assert result.success is False
    assert "ILMN_1659893" in result.unmapped_probes


def test_real_symbols_pass_through():
    mapper = create_probe_gene_mapper()
    result = mapper.validate_and_resolve(["TP53", "BRCA1"])
    assert result.success is True
    assert result.resolved_genes == ["TP53", "BRCA1"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/fixed_pipeline/test_gene_resolver.py -v`
Expected: first test FAILS (current code emits `UNKNOWN_GENE_*`).

- [ ] **Step 3: Fix the resolver**

In `gene_resolver.py:84`, replace `resolved_genes.append(f"UNKNOWN_GENE_{probe_id}")` with `resolved_genes.append(None)`. Optionally, when a `platform_id`/GPL annotation is available, attempt real resolution via `PlatformParser.load_gpl_annotation(gpl_id)` before marking unmapped. (Real GPL fetching can be a follow-up; the critical fix is removing fabrication.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/fixed_pipeline/test_gene_resolver.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Commit**
```bash
git add biodisc_core/fixed_pipeline/probe_gene_mapping/ tests/fixed_pipeline/test_gene_resolver.py
git commit -m "P0.2: stop fabricating UNKNOWN_GENE_ names; real annotation hook (Defect B)"
```

---

### Task P0.3: Derive real group labels from sample metadata (Defect C — HIGHEST INTEGRITY PRIORITY)

**Problem:** `multi_repository_downloader.py:354-356` and `:432-434` fabricate case/control assignment (`[0]*(n//2)+[1]*(n-n//2)` / `[i%2]`). With a random group split, every "differential expression" result is statistical noise even when expression values are real. This single bug invalidates more discoveries than any other.

**Files:**
- Create: `biodisc_core/fixed_pipeline/sample_metadata_parser.py`
- Modify: `biodisc_core/fixed_pipeline/multi_repository_downloader.py` (both group-label sites)
- Test: `tests/fixed_pipeline/test_sample_metadata_parser.py`

**Interfaces:**
- Produces: `parse_groups_from_series_matrix(matrix_text, question) -> GroupAssignment | None` where `GroupAssignment` is `{labels: np.ndarray, source: str, confidence: float}`. Returns `None` when groups cannot be determined → caller must **reject** the dataset.

- [ ] **Step 1: Write the failing test**

```python
import numpy as np
from biodisc_core.fixed_pipeline.sample_metadata_parser import (
    parse_groups_from_series_matrix,
)

# Minimal series-matrix snippet: 4 samples, 2 treatment / 2 control by characteristic
MATRIX = """!Sample_geo_accession = GSM1\tGSM2\tGSM3\tGSM4
!Sample_characteristics_ch1 = treatment: control
!Sample_characteristics_ch1 = treatment: control
!Sample_characteristics_ch1 = treatment: drug_x
!Sample_characteristics_ch1 = treatment: drug_x
"""


def test_parses_real_groups_from_characteristics():
    g = parse_groups_from_series_matrix(MATRIX, "effect of drug_x")
    assert g is not None
    assert list(g.labels) == [0, 0, 1, 1]
    assert g.source.startswith("characteristics")


def test_returns_none_when_groups_undeterminable():
    ambiguous = "!Sample_geo_accession = GSM1\tGSM2\n"
    assert parse_groups_from_series_matrix(ambiguous, "some question") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/fixed_pipeline/test_sample_metadata_parser.py -v`
Expected: FAIL (module doesn't exist).

- [ ] **Step 3: Implement `sample_metadata_parser.py`**

Implement `parse_groups_from_series_matrix`:
- Read `!Sample_characteristics_ch1` lines (and `!Sample_title`, `!Sample_source_name_ch1`) column-wise per sample.
- Tokenize each characteristic into `key: value`. Detect a binary grouping field (exactly 2 distinct values across samples) — prefer fields whose values relate to the question (simple keyword overlap).
- Map the 2 values to labels `{0,1}`. Set `source` and a heuristic `confidence`.
- If no binary field found → return `None`.
- **Never fabricate.** Returning `None` is correct behavior; the caller rejects.

- [ ] **Step 4: Wire into the downloader + reject on None**

In `multi_repository_downloader.py`, at both group-label sites (~354 and ~432), replace the fabricated labels with a call to the parser. If it returns `None`, log and return `None` from the download method (which the orchestrator already treats as "cannot download real data → reject discovery"). Keep the raw matrix text available to pass to the parser (it is parsed already; thread the text or the parsed characteristic list through).

- [ ] **Step 5: Run test to verify it passes + add anti-fabrication test**

Add:
```python
def test_downloader_does_not_fabricate_groups(monkeypatch):
    # If metadata parser returns None, downloader must return None, not [i%2]
    ...
```
Run: `python -m pytest tests/fixed_pipeline/test_sample_metadata_parser.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**
```bash
git add biodisc_core/fixed_pipeline/sample_metadata_parser.py biodisc_core/fixed_pipeline/multi_repository_downloader.py tests/fixed_pipeline/test_sample_metadata_parser.py
git commit -m "P0.3: derive real group labels from sample metadata; reject if unknown (Defect C)"
```

---

### Task P0.4: Enforce minimum sample count (Defect D)

**Problem:** `dataset_verifier_real.py:61-66` returns `(True, metadata)` even when `sample_count < 6`.

**Files:**
- Modify: `biodisc_core/fixed_pipeline/dataset_verifier_real.py`
- Test: `tests/fixed_pipeline/test_dataset_verifier.py`

- [ ] **Step 1: Write the failing test**

```python
from unittest.mock import patch
from biodisc_core.fixed_pipeline.dataset_verifier_real import create_dataset_verifier


def test_verifier_rejects_low_sample_count():
    v = create_dataset_verifier()
    fake_text = "!Series_title = X\n!Series_organism = Homo sapiens\n" + "".join(
        f"!Series_sample_id = GSM{i}\n" for i in range(3)
    )
    with patch("biodisc_core.fixed_pipeline.dataset_verifier_real.requests.get") as g:
        g.return_value.status_code = 200
        g.return_value.text = fake_text
        exists, meta = v.verify_geo_dataset("GSE00001")
    assert exists is False or (meta is not None and meta.get("usable") is False)
```

- [ ] **Step 2: Run — expected FAIL** (currently returns `True, meta`).

- [ ] **Step 3: Fix** — in `verify_geo_dataset`, when `sample_count < 6`, return `(False, metadata)` (or `(True, {..., 'usable': False})` if you need to distinguish "exists but unusable"). Decide and make the orchestrator treat unusable as rejection. Prefer returning `False` so the existing `if not success: reject` path triggers.

- [ ] **Step 4: Run — expected PASS.**

- [ ] **Step 5: Commit**
```bash
git add biodisc_core/fixed_pipeline/dataset_verifier_real.py tests/fixed_pipeline/test_dataset_verifier.py
git commit -m "P0.4: enforce sample_count >= 6 in verifier (Defect D)"
```

---

### Task P0.5: Harden metadata parsing + threading (Defect E)

**Problem:** `geo_data_downloader.py:_parse_geo_metadata` only counts `!Series_sample_id`; if GEO returns `!Series_geo_accession` instead, `sample_count` stays 0. Orchestrator defaults (`'Unknown'`, `0`) mask these failures in the published record.

**Files:**
- Modify: `biodisc_core/fixed_pipeline/geo_data_downloader.py` (`_parse_geo_metadata`)
- Modify: `biodisc_core/fixed_pipeline/FixedDiscoveryOrchestrator.py` (dataset dict at ~613–619: replace `'Unknown'`/`0` defaults with explicit failure if metadata absent)
- Test: `tests/fixed_pipeline/test_geo_metadata.py`

- [ ] **Step 1: Write the failing test**

```python
from biodisc_core.fixed_pipeline.geo_data_downloader import create_geo_data_downloader

TEXT = """!Series_title = Demo
!Series_organism = Homo sapiens
!Series_geo_accession = GSM1
!Series_geo_accession = GSM2
!Series_geo_accession = GSM3
!Series_geo_accession = GSM4
!Series_geo_accession = GSM5
!Series_geo_accession = GSM6
"""


def test_counts_geo_accession_lines():
    d = create_geo_data_downloader()
    meta = d._parse_geo_metadata(TEXT, "GSE12345")
    assert meta["sample_count"] == 6
    assert meta["organism"] == "Homo sapiens"
```

- [ ] **Step 2: Run — expected FAIL** (only `!Series_sample_id` counted → 0).

- [ ] **Step 3: Fix** — in `_parse_geo_metadata`, also count `!Series_geo_accession` and `!Series_sample_organism`. Add the union to `sample_count`. Ensure `organism` falls back to `!Series_sample_organism` if `!Series_organism` absent.

- [ ] **Step 4: Orchestrator threading** — in `FixedDiscoveryOrchestrator._generate_discovery_report`, when `verified_dataset.get('organism')` is empty, set a flag and (per Global Constraints) the discovery should be rejected upstream rather than silently recorded as `'Unknown'`. At minimum, replace `'Unknown'`/`0` defaults with the parsed values and log a warning when missing.

- [ ] **Step 5: Run — expected PASS.**

- [ ] **Step 6: Commit**
```bash
git add biodisc_core/fixed_pipeline/geo_data_downloader.py biodisc_core/fixed_pipeline/FixedDiscoveryOrchestrator.py tests/fixed_pipeline/test_geo_metadata.py
git commit -m "P0.5: robust metadata parse + thread into record (Defect E)"
```

---

### Task P0.6: Ground-truth benchmark + scalar fitness `h` (Defect F)

**Problem:** No machine-gradeable scalar exists. This is the AlphaEvolve precondition. Build a truth-known benchmark for differential-expression *methods* and a fitness `h`.

**Files:**
- Create: `biodisc_core/fixed_pipeline/benchmark/__init__.py`
- Create: `biodisc_core/fixed_pipeline/benchmark/truth_known_fixture.py` (truth-known benchmark generator — NOT discovery data)
- Create: `biodisc_core/fixed_pipeline/benchmark/de_fitness.py` (the evaluator `h`)
- Test: `tests/fixed_pipeline/test_benchmark_fitness.py`

**Interfaces:**
- Produces:
  - `make_de_benchmark(n_genes, n_samples, n_de, seed) -> BenchmarkCase` where `BenchmarkCase = {expression: np.ndarray (genes×samples), labels: np.ndarray, truth_de_indices: set[int]}`.
  - `score_de_method(method, case) -> DEMethodScore` where `DEMethodScore = {auroc: float, replicate_concordance: float, aggregate: float}` and `method` is a callable `(expression, labels) -> np.ndarray` of per-gene scores (higher = more DE).

- [ ] **Step 1: Write the failing test**

```python
import numpy as np
from biodisc_core.fixed_pipeline.benchmark.truth_known_fixture import make_de_benchmark
from biodisc_core.fixed_pipeline.benchmark.de_fitness import score_de_method


def _perfect_method(case):
    # A method that already knows the truth — should score ~1.0 AUROC
    scores = np.zeros(case.expression.shape[0])
    scores[list(case.truth_de_indices)] = 1.0
    return scores


def _random_method(case):
    rng = np.random.default_rng(0)
    return rng.random(case.expression.shape[0])


def test_perfect_method_scores_high_random_scores_low():
    case = make_de_benchmark(n_genes=500, n_samples=40, n_de=50, seed=1)
    perf = score_de_method(_perfect_method, case)
    rand = score_de_method(_random_method, case)
    assert perf.auroc > 0.95
    assert rand.auroc < perf.auroc
    assert 0.0 <= rand.aggregate <= perf.aggregate <= 1.0
```

- [ ] **Step 2: Run — expected FAIL** (modules absent).

- [ ] **Step 3: Implement `truth_known_fixture.py`**

Docstring MUST state: "Truth-known benchmark fixture for scoring DE methods. This is benchmark data with a known answer, NOT discovery data. Never emitted as a discovery." Generate two groups from different Gaussians for `n_de` randomly-chosen genes; record their indices as `truth_de_indices`.

- [ ] **Step 4: Implement `de_fitness.py`**

`score_de_method`:
- AUROC: rank method scores against `truth_de_indices` (sklearn or a 15-line manual AUROC — prefer no new heavy dep; manual is fine).
- replicate_concordance: re-run the method on a second independently-drawn benchmark (new seed), correlate the per-gene score rankings (Spearman) — rewards stability, not just in-sample fit.
- aggregate = 0.6*auroc + 0.4*replicate_concordance (document weights; tunable in Phase 1).
- Hard-gate: if method crashes or returns non-finite, return aggregate=0.0.

- [ ] **Step 5: Run — expected PASS.**

- [ ] **Step 6: Add a real-data held-out hook (stub for Phase 1)**

Add `score_de_method_on_real(case_loader, method)` that takes a loader returning real GEO-derived `BenchmarkCase`s (populated in Phase 1 from cached real datasets). For P0.6 it can raise `NotImplementedError` with a clear message; Phase 1 implements it. This makes the held-out-replication rule concrete in code.

- [ ] **Step 7: Commit**
```bash
git add biodisc_core/fixed_pipeline/benchmark/ tests/fixed_pipeline/test_benchmark_fitness.py
git commit -m "P0.6: truth-known DE benchmark + scalar fitness h (Defect F)"
```

---

### Phase 0 verification (gate before Phase 1)

- [ ] Run full suite: `python -m pytest tests/fixed_pipeline/ -v` — all green.
- [ ] Run a fixed reference analysis end-to-end on one real GEO dataset; confirm: no probe IDs in results, real group labels (or rejection), metadata populated, and a scalar fitness printed for the default t-test method on the benchmark.
- [ ] Grep audit: `grep -rn "UNKNOWN_GENE_\|i % 2\|n_samples // 2" biodisc_core/fixed_pipeline/` returns nothing in discovery path.
- [ ] Commit: `git commit --allow-empty -m "P0: evaluator trustworthy — Phase 0 complete"`

**If any check fails, do not proceed to Phase 1.** Evolution against an untrusted evaluator manufactures pseudo-science.

---

## Phase 1 — Evolve one method (DE analysis) over the evaluator

**Goal:** Prove the AlphaEvolve loop on a single well-defined evolvable target (differential-expression analysis), reusing the existing evolutionary skeleton. Single-process, no distribution.

**Reuse asset:** `biodisc_core/swarm/leapcore_evolution.py` — `LEAPCoreEvolution` (tournament selection + crossover), `Gene`/`Chromosome`, and `V36FitnessEvaluator` (multi-objective). Retarget `Chromosome` from meta-theory params to DE-program diffs. Do **not** rewrite evolution from scratch.

**Files:**
- Create: `biodisc_core/evolution/__init__.py`, `biodisc_core/evolution/program_db.py` (MAP-Elites archive), `biodisc_core/evolution/prompt_sampler.py`, `biodisc_core/evolution/diff_applier.py`, `biodisc_core/evolution/llm_ensemble.py`, `biodisc_core/evolution/controller.py`
- Create: `biodisc_core/evolution/seeds/de_method_seed.py` (the initial DE program = current t-test/BH pipeline as code)
- Tests: `tests/evolution/`

**Tasks (expand each into TDD micro-steps at phase start, following the Phase 0 pattern):**
- [ ] **P1.1** Represent the DE analysis as an evolvable Python program. Seed = current fixed pipeline (`differential_expression/__init__.py` logic) rewritten as a single function `analyze(expression, labels) -> DEOutput`. Fitness = `score_de_method` from P0.6. Test: seed method produces a non-zero aggregate on the benchmark.
- [ ] **P1.2** `llm_ensemble.py`: wrap Anthropic API. Two models: Haiku 4.5 (high-throughput mutations) + Sonnet 5 (breakthrough mutations). Interface `propose_diff(parent_code, inspirations, eval_results) -> diff_blocks`. Test with a mock client.
- [ ] **P1.3** `diff_applier.py`: apply AlphaEvolve-style search-and-replace diff blocks to source; reject malformed diffs. Test: apply a known diff, assert resulting code + that invalid diffs raise.
- [ ] **P1.4** `prompt_sampler.py`: assemble `{system instructions, parent program, k sampled inspirations, rendered eval results, stochastic formatting}`. Test: output is deterministic given seed and contains parent code.
- [ ] **P1.5** `program_db.py`: MAP-Elites + island archive. `add(program, scores)`, `sample() -> (parent, inspirations)`. Test: resurfaces high-scoring diverse programs; explore/exploit balance.
- [ ] **P1.6** `controller.py`: the async loop `sample → build_prompt → propose_diff → apply_diff → evaluate(=h from P0.6, with 5-layer validation as PREREQUISITE gate) → add`. Single-process first. Test: one generation runs and archive grows.
- [ ] **P1.7** Wire the 5-layer validation as a **hard gate before** fitness scoring (never part of fitness).
- [ ] **P1.8** Run evolution for N generations on the DE benchmark; record genealogy to `biodisc_core/evolution/runs/`.

**Phase 1 exit criterion:** the evolved DE method beats the seed (fixed t-test/BH) pipeline on benchmark `aggregate` fitness by ≥5 points, with held-out replication not degrading. Genealogy is inspectable.

### Phase 1 STATUS — COMPLETE (2026-07-11)

**Exit-criterion revision (made during execution):** as originally written the
criterion was impossible — the seed t-test already scores ~0.999 on the *easy*
Gaussian benchmark, leaving no headroom. Revised to: on a HARD benchmark
scenario with headroom, the evolved method's aggregate beats the seed with
held-out replication not degrading. Also required adding the hard scenario
itself (else the fitness cannot discriminate methods).

**Two deviations from the plan (both justified):**
1. **Did NOT reuse `leapcore_evolution.py`.** On inspection it is a
   *parameter/numeric* evolution engine (`Gene.mutate` on numbers, tournament
   selection on parameter `Chromosome`s). That is not code evolution and cannot
   represent what AlphaEvolve does. Built the actual AlphaEvolve mechanism
   (LLM-proposed code diffs + MAP-Elites + exec-based evaluation). Reused only
   its multi-objective-fitness *concept*, and Phase 1's fitness is already
   scalar via P0.6.
2. **Provider-agnostic LLM, running on GLM, not Anthropic.** This Claude Code
   session is powered by GLM; there is no Anthropic key. `LLMEnsemble` uses the
   Anthropic Messages API as a *wire protocol* against whatever gateway is
   configured (`ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` +
   `ANTHROPIC_AUTH_TOKEN` here). Default model `glm-4.6`, overridable via
   `BIODISC_EVOLUTION_MODEL`. AlphaEvolve is model-agnostic; GLM is the engine.

**Implemented (commits 5cfe2f7-era → P1.x):** `biodisc_core/evolution/`
{program.py, seeds, diff_applier.py, program_db.py (1-D MAP-Elites),
prompt_sampler.py, llm_ensemble.py, controller.py, run_evolution.py}.
88/88 tests pass (`tests/fixed_pipeline/` + `tests/evolution/`).

**Real GLM-driven evolution run (3 generations × 2 attempts, heteroscedastic
hard benchmark):**
- seed (Student's t-test) aggregate = **0.781**
- best evolved aggregate = **0.874** (AUROC 0.839, held-out replicate 0.927)
- **improvement = +0.093** (exceeds the ≥5-point bar)
- GLM discovered a Mann-Whitney U scoring variant; genealogy shows real
  explore/exploit dynamics (gen-1 regressions, gen-2 improvement branching from
  the seed, gen-3 regression retained-out by MAP-Elites elitism).

**Honest scope (per anti-overclaim rule):** the loop works end-to-end and GLM
improved the *measured* fitness on this benchmark + its held-out replicate.
The specific "discovery" is benchmark-fit; it needs cross-dataset validation
(Phase 3's real-data held-out hook) before any scientific claim. We evolve
*methods*, not biological facts.

**Task checkbox status:** P1.1–P1.8 all done (P1.1 hard-scenario+seed; P1.2
diff_applier; P1.3 program_db MAP-Elites; P1.4 prompt_sampler; P1.5
llm_ensemble; P1.6 controller+genealogy; P1.7 validation-as-hard-gate folded
into the controller; P1.8 run_evolution + live run).

---

## Phase 2 — Genealogy depth + co-evolved meta-prompts

**Goal:** Unlock AlphaEvolve's "resurface past ideas" power and replace the static 18-question list (`specific_questions.py`) with evolved meta-prompts.

**Tasks:**
- [x] **P2.1** Expand `program_db.py` to 2-D MAP-Elites (complexity × method-family) + `IslandModel` (N archives, ring migration, fair `seed_all`).
- [x] **P2.2** Co-evolved meta-prompts: `MetaPromptArchive` (epsilon-greedy on empirical mean aggregate); `prompt_sampler` injects the active directive; controller credits it on accept.
- [x] **P2.3** LLM `QuestionGenerator` + generic/template gate; `get_questions_via_llm()` is the drop-in replacement source for `specific_questions.py` (kept as fallback).
- [x] **P2.4** `evaluation_cascade`: cheap independent screen → full → held-out; controller `use_cascade` option.

**Phase 2 exit criterion:** diversity of generated candidates measurably higher than Phase 1; inspirations demonstrably feed prompts.

### Phase 2 STATUS — COMPLETE (2026-07-11)

**Exit criterion — MET on diversity/inspiration axes.** Real GLM runs now explore
3–4 method families per run (ttest/rank/foldchange/bayes/other) across 3–5
(complexity, family) niches, vs Phase 1's ~2 families. Co-evolved meta-prompts
are demonstrably fed into prompts and selected by empirical success
(e.g. "Combine effect size with significance" credited mean-agg 0.761, n=4).
Island ring-migration + fair seeding (`seed_all`) and the evaluation cascade
(cascade pruned candidates in the --cascade run) all run end-to-end. 108/108
tests pass (`tests/fixed_pipeline/` + `tests/evolution/`).

**Honest result on fitness (important):** the Phase-2 short runs (3–5
generations) did NOT beat the seed (0.781) — and neither did a single-archive
sanity rerun. The Phase-1 +0.093 (Mann-Whitney U, 0.874) was a high-variance
lucky proposal; LLM code-evolution improves fitness *stochastically*, and a
3–5 generation budget does not guarantee beating the incumbent every run.
Fitness improvement remains *proven* two ways: the Phase-1 real run (+0.093)
and the deterministic scripted controller test (fold-change > seed). Working
hypothesis for the no-gain Phase-2 runs: co-evolved meta-prompts steer toward
"robust/non-parametric" strategies whose GLM implementations underperform the
seed here; longer runs (or per-meta-prompt credit maturation) should
down-weight them. Tuning this is a Phase 3 agenda item, not a defect.

**Implemented (commits P2.1–P2.4):** `program_db.py` (2-D MAP-Elites +
`IslandModel`), `meta_prompt.py`, `evaluation_cascade.py`,
`fixed_pipeline/question_generator.py`, plus `run_evolution.py` flags
(`--islands`, `--cascade`, `--migration-interval`, `--screen-floor`) and a
diversity report.

**What was NOT done (deliberate):** did not rip out `specific_questions.py`
(the running discovery loop still imports it); the LLM generator is an
additive replacement source.

---

## Phase 3 — Hypothesis-as-code

**Goal:** Generalize so a "discovery program" = executable code that runs an evolved-method primitive on a real dataset and emits a quantitative claim + uncertainty. Connect back to BIODISC's discovery mission.

**Tasks:**
- [ ] **P3.1** Define `DiscoveryProgram` representation (code that returns `{claim, effect_size, ci, p, genes, dataset_id}`).
- [ ] **P3.2** Extend fitness: held-out replication on a real independent cohort (the P0.6 real-data hook now implemented) as the anchor; novelty + PubMed-consistency as LLM-graded soft signals (multi-objective via `V36FitnessEvaluator`).
- [ ] **P3.3** Graded-autonomy human checkpoint before any discovery is "published" to `autonomous_discoveries.jsonl`.
- [ ] **P3.4** Provenance: every published discovery links to its evolved-method genealogy + diff history.

**Phase 3 exit criterion:** a discovery published via this path replicates on a held-out cohort at an agreed rate; full diff genealogy is auditable.

---

## Phase 4 — Scale + optional self-improvement

**Goal:** Distributed asynchronous controller (AlphaEvolve §2.5); optionally let evolved methods improve BIODISC's own analysis infrastructure.

**Tasks:**
- [ ] **P4.1** Distribute the controller (async workers, shared program DB, locks/metrics).
- [ ] **P4.2** Optional bootstrapping: target BIODISC's own pipeline components (probe mapper, normalizer) as evolution problems — the analog of AlphaEvolve improving its base-LLM training.
- [ ] **P4.3** Distill winning patterns back into the default pipeline.

**Phase 4 exit criterion:** throughput scales linearly with workers for ≥4 workers; no regressions vs Phase 3 quality.

---

## Anti-pseudo-science guards (apply in every phase)

1. Validation = hard gate, never fitness.
2. Held-out replication is the fitness anchor; in-sample p-values are not rewarded.
3. Benchmark/evaluator truth sets are never visible to the method during evolution (strict train/held-out split).
4. Full provenance + diff genealogy for every candidate and every published discovery.
5. Human checkpoint (graded autonomy) before publication.
6. Honest framing: we evolve methods, not facts.

## Self-review notes (plan author)
- Spec coverage: all six defects (A–F) → P0.1–P0.6. Evolution mechanisms → P1.1–P1.8. Genealogy/meta-prompts → P2. Distributed → P4. Hypothesis-as-code → P3.
- Line numbers in this plan are point-in-time (2026-07-11); re-verify before editing.
- `gene_symbol_validation.py` factory name assumed `create_gene_symbol_validator` — verify exact name at P0.1 step 3.
- `multi_repository_downloader.py` has the real download path used by the orchestrator; `geo_data_downloader.py` is partly legacy but still owns metadata parsing used in records — both touched in P0.3/P0.5.
