# Molecular Complexity Threshold: Experimentalist's Quick Reference

**Purpose:** Practical guide for testing the molecular complexity threshold hypothesis
**For:** Experimental biologists, graduate students, postdocs

---

## The Core Claim (in 3 sentences)

1. **Bacteria need ~45 cell cycle genes** to achieve precise division (CV < 0.20)
2. **Below this threshold**, division timing becomes highly variable (CV > 0.35) and placement errors exceed 15%
3. **Regulatory genes matter more** than total gene count - TFs, two-component systems, and checkpoint genes have disproportionate impact

---

## Key Metrics to Measure

### Essential Metrics (Required)

**1. Division Precision**
- **What to measure:** Coefficient of variation (CV) of division timing
- **How:** Single-cell time-lapse microscopy, n > 300 cells
- **Thresholds:**
  - CV < 0.20: Precise (above threshold)
  - CV 0.20-0.35: Transition zone
  - CV > 0.35: Imprecise (below threshold)

**2. Division Placement Accuracy**
- **What to measure:** Percentage of cells with septum at midcell ± 10%
- **How:** Fluorescent membrane stain, measure septum position
- **Thresholds:**
  - < 5% errors: Precise (wild-type)
  - 5-15% errors: Moderate
  - > 15% errors: Imprecise (minimal cell)

**3. Cell Cycle Gene Count (CCGC)**
- **What to count:** Genes involved in replication, division, segregation, checkpoints
- **How:** Genome annotation + literature curation
- **Categories:**
  - Replication: dnaA, dnaB, dnaC, dnaN, dnaX, dnaE, etc.
  - Division: ftsZ, ftsA, ftsQ, ftsL, ftsB, ftsW, ftsI, ftsN, zipA, zapA
  - Segregation: parA, parB, smc, mukB, mukE, mukF, topoisomerases
  - Regulation: minC, minD, minE, slmA, noc, sulA, seqA, etc.

### Optional Metrics (For deeper analysis)

**4. Regulatory Gene Density (RGD)**
- Formula: RGD = (TFs + TCS + sigma factors) / total genes
- Threshold: RGD ≈ 0.14

**5. Network Connectivity**
- Requires: Protein-protein interaction data or regulatory network
- Metric: Average edges per node
- Threshold: ~2.5 interactions per gene

---

## Quick Experimental Protocols

### Protocol 1: Measure Division Precision (2 days)

**Day 1: Setup**
1. Grow overnight culture of your strain
2. Dilute 1:100 into fresh medium
3. Load into microfluidic device or agarose pad

**Day 2: Imaging**
1. Image every 2-3 minutes for 6-8 hours
2. Use phase contrast for cell boundaries
3. Track >300 individual cells

**Analysis:**
```python
# Pseudocode
for each cell:
    record division_times
    calculate mean_division_time
    calculate CV = std / mean
report CV with confidence_interval
```

**Expected Results:**
- Wild-type E. coli: CV = 0.10-0.15
- syn3.0: CV = 0.35-0.45
- Your strain: Compare to threshold (0.20)

### Protocol 2: Count Cell Cycle Genes (1 week)

**Step 1: Download Genome**
- Use NCBI or Ensembl Bacteria
- Annotated genome in GenBank or GFF format

**Step 2: Extract Annotations**
```bash
# Example for E. coli
grep -i "dnaA\|dnaB\|dnaC\|ftsZ\|ftsA\|minC\|minD" genome.gff
```

**Step 3: Manual Curation**
- Use databases: EcoCyc, UniProt, KEGG
- Literature search for known cell cycle genes
- Create spreadsheet with categories

**Step 4: Verify**
- BLAST unknown genes against known cell cycle genes
- Check operons and gene neighborhoods
- Consult with experts if needed

**Deliverable:**
- Spreadsheet with gene names, functions, categories
- Total CCGC count
- Comparison to threshold (45 genes)

### Protocol 3: Systematic Gene Deletion (6 months)

**Overview:**
- Start with syn3.0 or minimal strain
- Delete 2-3 genes at a time
- Create 10-15 strains with decreasing CCGC
- Measure division precision for each

**Strategic Gene Deletion Order:**
1. **Non-essential regulators** (minC, minD, minE, slmA)
2. **Non-essential division proteins** (zapA, zapB)
3. **Checkpoint genes** (sulA, seqA)
4. **Non-essential segregation proteins** (mukE, mukF)
5. **Carefully**: Partially essential genes (titratable promoters)

**Controls:**
- Always keep ftsZ (essential)
- Keep dnaA, dnaB, dnaC (essential for replication)
- Monitor growth rate
- Check for viability

**Measurement:**
- For each strain: measure CV (Protocol 1)
- Plot: CV vs. CCGC
- Identify threshold where CV sharply increases

### Protocol 4: Gene Addition (3 months)

**Overview:**
- Start with minimal strain (low CCGC)
- Add specific gene sets
- Test which improve precision most

**Gene Sets to Test:**
- Set A (TFs): Add 10 transcription factors from E. coli
- Set B (TCS): Add 5 two-component systems
- Set C (Checkpoint): Add sulA, seqA, and regulators
- Set D (Control): Add 10 metabolic genes

**Cloning Strategy:**
- Use inducible promoters
- Test expression levels
- Verify protein production (Western blot)

**Expected Results:**
- Regulatory sets (A, B, C): CV improvement Δ > 0.10
- Metabolic set (D): CV improvement Δ < 0.05
- Checkpoint genes: Largest effect on placement accuracy

---

## Data Analysis Templates

### Template 1: Calculate CV from Single-Cell Data

```python
import numpy as np
import pandas as pd
from scipy import stats

# Load data (columns: cell_id, division_time)
data = pd.read_csv('division_times.csv')

# Calculate CV
mean_dt = data['division_time'].mean()
std_dt = data['division_time'].std()
cv = std_dt / mean_dt

# Bootstrap confidence interval
n_bootstrap = 10000
cv_bootstrap = []
for i in range(n_bootstrap):
    sample = data['division_time'].sample(n=len(data), replace=True)
    cv_boot = sample.std() / sample.mean()
    cv_bootstrap.append(cv_boot)

ci_low = np.percentile(cv_bootstrap, 2.5)
ci_high = np.percentile(cv_bootstrap, 97.5)

print(f"CV = {cv:.3f} [{ci_low:.3f}, {ci_high:.3f}]")
print(f"n = {len(data)} cells")

# Compare to threshold
if cv < 0.20:
    status = "PRECISE (above threshold)"
elif cv < 0.35:
    status = "TRANSITION (near threshold)"
else:
    status = "IMPRECISE (below threshold)"
print(f"Status: {status}")
```

### Template 2: Fit Hyperbolic Decay Model

```python
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Hyperbolic decay model
def hyperbolic_decay(C, cv_min, cv_max, c_half, n):
    return cv_min + (cv_max - cv_min) / (1 + (C / c_half)**n)

# Your data: CCGC values and corresponding CVs
ccgc = np.array([19, 30, 45, 60, 80, 120, 200])
cv = np.array([0.42, 0.35, 0.28, 0.22, 0.17, 0.14, 0.12])

# Fit model
params, covariance = curve_fit(hyperbolic_decay, ccgc, cv,
                               p0=[0.12, 0.45, 45, 2.3],
                               bounds=([0, 0, 10, 1], [0.5, 1.0, 100, 5]))

cv_min, cv_max, c_half, n = params
print(f"CV_min = {cv_min:.3f}")
print(f"CV_max = {cv_max:.3f}")
print(f"C_half = {c_half:.1f}")
print(f"n = {n:.2f}")

# Plot
C_range = np.linspace(10, 250, 100)
cv_fit = hyperbolic_decay(C_range, *params)

plt.figure(figsize=(10, 6))
plt.scatter(ccgc, cv, s=100, label='Data', zorder=5)
plt.plot(C_range, cv_fit, 'r-', label='Fit', linewidth=2)
plt.axhline(y=0.20, color='gray', linestyle='--', label='Precision threshold')
plt.axvline(x=c_half, color='gray', linestyle=':', label=f'C_half = {c_half:.1f}')
plt.xlabel('Cell Cycle Gene Count (CCGC)', fontsize=14)
plt.ylabel('Division Timing CV', fontsize=14)
plt.legend(fontsize=12)
plt.title('Precision vs. Molecular Complexity', fontsize=16)
plt.savefig('precision_complexity_curve.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Template 3: Compare Gene Sets (ANOVA)

```python
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Data: strain, gene_set, CV
data = pd.DataFrame({
    'strain': ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'],
    'gene_set': ['TF'] * 3 + ['TCS'] * 3 + ['Control'] * 3,
    'CV': [0.18, 0.19, 0.20, 0.17, 0.18, 0.19, 0.35, 0.36, 0.34]
})

# ANOVA
model = ols('CV ~ gene_set', data=data).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

# Post-hoc tests
from scipy.stats import tukey_hsd
result = tukey_hsd(data[data['gene_set'] == 'TF']['CV'],
                   data[data['gene_set'] == 'TCS']['CV'],
                   data[data['gene_set'] == 'Control']['CV'])
print(result)
```

---

## Expected Results Reference

### Reference Values for Common Strains

| Strain | CCGC | CV (Timing) | Placement Error % | Status |
|--------|------|-------------|-------------------|---------|
| E. coli WT | ~200 | 0.10-0.15 | < 5% | Above threshold |
| B. subtilis WT | ~180 | 0.12-0.18 | < 5% | Above threshold |
| Caulobacter | ~150 | 0.08-0.12 | < 5% | Above threshold |
| syn3.0 | 19 | 0.35-0.45 | 15-20% | Below threshold |
| Mycoplasma | ~20 | ~0.40 | ~20% | Below threshold |

### What Your Results Mean

**If CV < 0.20:**
- Your strain is above threshold
- Molecular regulation is functioning
- Precise division achieved

**If 0.20 < CV < 0.35:**
- Your strain is near threshold
- Mixed physical/molecular control
- Interesting transition zone

**If CV > 0.35:**
- Your strain is below threshold
- Physical tendencies dominate
- Consider adding regulatory genes

**If Placement Error > 15%:**
- Spatial regulation compromised
- Min system or nucleoid occlusion likely affected
- Check for division site selection genes

---

## Common Pitfalls to Avoid

### Pitfall 1: Too Few Cells
- **Problem:** n < 200 cells gives unreliable CV estimates
- **Solution:** Always measure >300 cells per strain
- **Rule of thumb:** CV SE ≈ CV / sqrt(2n)

### Pitfall 2: Confounding Growth Rate
- **Problem:** Slow growth → artificially low CV
- **Solution:** Measure growth rate, include in analysis
- **Check:** Does your strain grow at >50% of wild-type rate?

### Pitfall 3: Environmental Variation
- **Problem:** Temperature, medium affect division timing
- **Solution:** Standardize conditions, use controls
- **Control:** Always include wild-type in same experiment

### Pitfall 4: Gene Misannotation
- **Problem:** Not all cell cycle genes are annotated
- **Solution:** BLAST search, manual curation
- **Verify:** Check expression data if available

### Pitfall 5: Essential Gene Deletion
- **Problem:** Deleting essential genes kills cells
- **Solution:** Use titratable promoters, partial knockdowns
- **Alternative:** Study hypomorphic alleles

---

## Sample Size Calculator

### For Detecting CV Differences

```python
from scipy import stats

def sample_size_for_cv(cv1, cv2, alpha=0.05, power=0.8):
    """
    Calculate sample size needed to detect difference between two CVs
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)

    n_per_group = 2 * ((z_alpha + z_beta) / (np.log(cv1/cv2)))**2
    return int(np.ceil(n_per_group))

# Example: Detect difference between syn3.0 (CV=0.40) and mutant (CV=0.30)
n = sample_size_for_cv(0.40, 0.30)
print(f"Need {n} cells per group")
```

### For Gene Count Correlation

```python
# Sample size for correlation test
def sample_size_for_correlation(r, alpha=0.05, power=0.8):
    """
    Calculate sample size needed to detect correlation r
    """
    from scipy.stats import fisher_exact
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)

    # Fisher's z transformation
    z = 0.5 * np.log((1 + r) / (1 - r))
    n = ((z_alpha + z_beta) / z)**2 + 3
    return int(np.ceil(n))

# Example: Detect r = -0.80 (strong correlation)
n = sample_size_for_correlation(-0.80)
print(f"Need {n} species"
```

---

## Troubleshooting Guide

### Problem: High variability in measurements

**Check:**
1. Are you tracking cells correctly?
2. Is imaging interval appropriate (2-3 min)?
3. Are there focus issues?
4. Is temperature stable?

**Solutions:**
- Use automated tracking software (e.g., Oufti, MicrobeTracker)
- Add focus stabilization
- Include environmental control
- Increase cell count

### Problem: No clear threshold

**Check:**
1. Did you sample enough complexity range?
2. Are gene annotations correct?
3. Is growth rate confounded?

**Solutions:**
- Extend range (more strains)
- Verify gene annotations
- Include growth rate as covariate
- Consider alternative metrics

### Problem: Unexpected results

**Check:**
1. Are strain genotypes correct?
2. Is contamination possible?
3. Are measurements consistent?

**Solutions:**
- Verify genotypes by PCR
- Include negative controls
- Repeat measurements
- Check with colleagues

---

## Quick Decision Tree

```
START: Have you measured your strain?
│
├─ NO → Follow Protocol 1 (measure CV)
│
└─ YES → CV < 0.20?
    │
    ├─ YES → Strain above threshold
    │         → Molecular regulation working
    │         → Consider mechanistic studies
    │
    └─ NO → CV < 0.35?
        │
        ├─ YES → Strain in transition zone
        │         → Interesting intermediate case
        │         → Study physical/molecular balance
        │
        └─ NO → Strain below threshold
                 → Physical tendencies dominate
                 → Consider adding regulatory genes (Protocol 4)
```

---

## Reporting Results

### Essential Information to Report

**For each strain:**
1. Genotype (deleted/added genes)
2. CCGC (with methodology)
3. Division timing CV (with CI, n cells)
4. Placement error % (with CI, n cells)
5. Growth rate
6. Measurement conditions

**For comparative studies:**
1. Statistical test used
2. Effect sizes
3. Confidence intervals
4. Sample sizes

**Figure suggestions:**
- CV vs. CCGC scatter plot with model fit
- Placement error vs. CCGC
- Growth rate vs. CCGC (check for confounding)
- Single-cell traces (representative examples)

---

## Contact and Resources

**For questions:**
- Statistical analysis: Consult with biostatistician
- Gene annotation: Use EcoCyc, UniProt databases
- Strain construction: See protocols in Methods section

**Useful software:**
- Image analysis: Oufti, MicrobeTracker, CellProfiler
- Statistical analysis: R, Python (statsmodels), GraphPad Prism
- Genome analysis: BLAST, Artemis, Geneious

**Key references:**
- Hutchison et al. (2016) syn3.0 design
- Taheri-Araghi et al. (2015) adder model
- Shi et al. (2018) cell-size control
- Breuer et al. (2019) minimal cell metabolism

---

**Last updated:** 2026-04-23
**Version:** 1.0

**Good luck with your experiments!**
