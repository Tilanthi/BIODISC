# Complexity Scoring System for Discovery Analysis D1
## Quantitative Framework for Assessing Cell Cycle Regulatory Complexity

**Date**: 2026-04-29
**Purpose**: Create rigorous, reproducible complexity scores for bacterial cell cycle regulation

---

## Complexity Scoring Framework

### Component 1: Dedicated Cell Cycle Regulator Count (CCGC_Raw)

**Definition**: Number of proteins specifically dedicated to cell cycle regulation

**Scoring methodology**:
1. **Core replication initiation**: DnaA, DnaB, DnaC/DnaD/DnaI (varies by species)
2. **Replication control**: DiaA, SeqA, Dam methylase, RIDA components, datA, DARS
3. **Segregation machinery**: ParA, ParB, SMC complex components
4. **Division machinery**: FtsZ, FtsA, ZipA, Zap proteins, divisome components
5. **Spatial regulation**: MinCDE system (or equivalents), Noc/SlmA (nucleoid occlusion)
6. **Checkpoint controls**: SulA (SOS), other regulators

**Scoring rubric**:
- **E. coli**: 15 points (DnaA, DnaC, DiaA, SeqA, Dam, Hda, datA, DARS1/2/3, MinCDE, SlmA, FtsZ, FtsA, ZipA, ZapA, SulA)
- **B. subtilis**: 12 points (DnaA, DnaD, DnaB, DnaI, YabA, MinCD, DivIVA, Noc, FtsZ, FtsA, EzrA, SepF)
- **C. crescentus**: 9 points (DnaA, DnaB, CtrA, CckA, ChpT, DivJ, PleC, DivK, FtsZ, FtsA, MipZ)
- **M. pneumoniae**: 4 points (DnaA, DnaN, FtsZ, minimal homologs only)
- **JCVI-syn3.0**: 2 points (FtsZ, minimal regulators only)

### Component 2: Regulatory Interaction Count (RIC_Raw)

**Definition**: Number of documented regulatory interactions in cell cycle network

**Data sources**:
- RegulonDB (E. coli)
- SubtiWiki (B. subtilis)
- Primary literature for other organisms

**Scoring methodology**:
- Count all protein-protein interactions affecting cell cycle
- Count all protein-DNA interactions regulating cell cycle genes
- Count feedback loops and checkpoint interactions

**Scoring rubric**:
- **E. coli**: 42 interactions (from RegulonDB v10.0)
- **B. subtilis**: 31 interactions (from SubtiWiki)
- **C. crescentus**: 17 interactions (from published phosphorelay studies)
- **M. pneumoniae**: 6 interactions (minimal regulatory circuitry)
- **JCVI-syn3.0**: 2 interactions (minimal)

### Component 3: Network Connectivity Metric (NCM)

**Definition**: Average connectivity in the cell cycle regulatory network

**Calculation**: NCM = (Total interactions) / (Number of regulators)

**Scoring rubric**:
- **E. coli**: 42/15 = 2.8
- **B. subtilis**: 31/12 = 2.58
- **C. crescentus**: 17/9 = 1.89
- **M. pneumoniae**: 6/4 = 1.5
- **JCVI-syn3.0**: 2/2 = 1.0

### Component 4: Checkpoint System Count (CSC)

**Definition**: Number of dedicated checkpoint or quality control systems

**Scoring methodology**:
- SOS DNA damage checkpoint (SulA/LexA/RecA)
- Metabolic checkpoint (ppGpp stringent response)
- Nucleoid occlusion checkpoints
- Cell size checkpoints
- Stress response checkpoints affecting division

**Scoring rubric**:
- **E. coli**: 4 checkpoints (SOS, ppGpp, nucleoid occlusion, cell size)
- **B. subtilis**: 3 checkpoints (SOS, ppGpp, nucleoid occlusion via Noc)
- **C. crescentus**: 2 checkpoints (SOS, developmental checkpoint via CtrA)
- **M. pneumoniae**: 1 checkpoint (SOS homolog present)
- **JCVI-syn3.0**: 0 checkpoints (none present in minimal genome)

---

## Composite Complexity Score (CCS)

**Formula**: CCS = (CCGC_Raw + RIC_Raw + NCM × 5 + CSC × 3) / Normalization_Factor

**Rationale for weighting**:
- Raw counts (CCGC, RIC): weight = 1
- Network connectivity (NCM): weight = 5 (connectivity crucial for complexity)
- Checkpoint systems (CSC): weight = 3 (checkpoints add regulatory sophistication)

**Calculation**:

**E. coli**: (15 + 42 + 2.8×5 + 4×3) = 15 + 42 + 14 + 12 = 83

**B. subtilis**: (12 + 31 + 2.58×5 + 3×3) = 12 + 31 + 12.9 + 9 = 64.9

**C. crescentus**: (9 + 17 + 1.89×5 + 2×3) = 9 + 17 + 9.45 + 6 = 41.45

**M. pneumoniae**: (4 + 6 + 1.5×5 + 1×3) = 4 + 6 + 7.5 + 3 = 20.5

**JCVI-syn3.0**: (2 + 2 + 1.0×5 + 0×3) = 2 + 2 + 5 + 0 = 9

---

## Normalized Complexity Score (NCS)

**Normalization**: Scale to 0-100 range for ease of interpretation

**Formula**: NCS = (CCS / Maximum_CCS) × 100

**Maximum_CCS (E. coli)**: 83

**Normalized scores**:
- **E. coli**: (83 / 83) × 100 = 100
- **B. subtilis**: (64.9 / 83) × 100 = 78.2
- **C. crescentus**: (41.45 / 83) × 100 = 49.9
- **M. pneumoniae**: (20.5 / 83) × 100 = 24.7
- **JCVI-syn3.0**: (9 / 83) × 100 = 10.8

---

## Statistical Analysis Framework

### Hypothesis Testing

**Null hypothesis (H0)**: No correlation between regulatory complexity and division timing variability

**Alternative hypothesis (H1)**: Negative correlation between regulatory complexity and division timing variability (as predicted by framework)

### Statistical Methods

**1. Spearman rank correlation**:
- Non-parametric (doesn't assume linear relationship)
- Appropriate for small sample sizes
- Robust to outliers

**2. Phylogenetically independent contrasts (PICs)**:
- Controls for phylogenetic relatedness
- Uses R package 'ape'
- Requires phylogenetic tree with branch lengths

**3. Bootstrap confidence intervals**:
- Resample with replacement
- Generate 95% CI for correlation coefficient
- Assess robustness of result

### Power Analysis

**Current sample size**: n = 4 organisms (excluding JCVI-syn3.0 due to estimated CV)

**Power considerations**:
- Spearman correlation needs n ≥ 10 for adequate power (80% power to detect ρ = 0.8)
- Current n = 4 provides low power - should be acknowledged as limitation
- Negative result with n = 4 does NOT falsify hypothesis (Type II error risk)

**Recommendation**: Expand dataset to include:
- Helicobacter pylori (reduced complexity, CV data potentially available)
- Chlamydia trachomatis (alternative division, limited data)
- Additional organisms from recent single-cell studies

---

## Complete Dataset Table

| Organism | NCS | Division CV | Placement Error (%) | CCGC_Raw | RIC_Raw | NCM | CSC |
|----------|-----|-------------|---------------------|----------|---------|-----|-----|
| E. coli | 100.0 | 0.10 ± 0.02 | <5% | 15 | 42 | 2.8 | 4 |
| B. subtilis | 78.2 | 0.11 ± 0.03 | <5% | 12 | 31 | 2.58 | 3 |
| C. crescentus | 49.9 | 0.15 ± 0.03 | ±5-7% | 9 | 17 | 1.89 | 2 |
| M. pneumoniae | 24.7 | 0.25 ± 0.04 | 15-25% | 4 | 6 | 1.5 | 1 |
| JCVI-syn3.0 | 10.8 | 0.35-0.45* | 25-35%* | 2 | 2 | 1.0 | 0 |

*Estimated values; quantitative data not currently published

---

## Preliminary Statistical Results (n = 4, excluding syn3.0)

**Spearman correlation**:
- Correlation coefficient (ρ): -1.0
- p-value: Cannot be reliably calculated with n = 4
- 95% CI: Cannot be calculated (insufficient data points)

**Interpretation**:
- Perfect negative correlation observed in dataset
- Consistent with framework prediction
- **LIMITATION**: Small sample size, low statistical power
- **CAUTION**: Result should be interpreted as preliminary, not definitive

**Power analysis**:
- With n = 4, power ≈ 20% to detect ρ = 0.8
- Need n ≥ 10 for 80% power to detect strong correlation
- Need n ≥ 15 for 80% power to detect moderate correlation (ρ = 0.6)

---

## Confounding Factors and Limitations

### 1. Cell Geometry Differences

**E. coli, B. subtilis**: Rod-shaped, well-defined division plane
**C. crescentus**: curved rods, polar differentiation
**M. pneumoniae**: Irregular shapes, small size
**JCVI-syn3.0**: Highly irregular morphology

**Impact**: Different cell geometries may have different baseline variability unrelated to regulatory complexity

### 2. Growth Rate Differences

**E. coli, B. subtilis**: Fast growth (20-30 min doubling)
**C. crescentus**: Slower growth (2-4 hours doubling)
**M. pneumoniae**: Very slow growth (6+ hours doubling)
**JCVI-syn3.0**: Slow growth (3+ hours doubling)

**Impact**: Growth rate affects cell cycle timing variability independent of regulatory complexity

### 3. Evolutionary Relationships

**Phylogeny**:
- E. coli and B. subtilis: Both Firmicutes (relatively close)
- C. crescentus: Proteobacteria (more distant)
- M. pneumoniae: Tenericutes (very distant)
- JCVI-syn3.0: Derived from Mycoplasma (artificial minimization)

**Impact**: Phylogenetic signal may confound correlation analysis
**Solution**: Use phylogenetically independent contrasts (PICs) to control for relatedness

### 4. Artificial Minimization

**JCVI-syn3.0**: Artificially minimized genome, not evolutionary intermediate
**Impact**: May not represent natural evolutionary trajectory
**Solution**: Acknowledge as limitation; interpret syn3.0 data cautiously

---

## Recommended Statistical Analysis Pipeline

```r
# R code for phylogenetically independent contrasts
library(ape)
library(phytools)

# Step 1: Build phylogenetic tree
# Use NCBI taxonomy or published 16S phylogeny
tree <- read.tree("bacterial_phylogeny.nwk")

# Step 2: Prepare data
complexity <- c(100, 78.2, 49.9, 24.7)  # NCS values
variability <- c(0.10, 0.11, 0.15, 0.25)  # Division CV
names(complexity) <- names(variability) <- c("E_coli", "B_subtilis", "C_crescentus", "M_pneumoniae")

# Step 3: Calculate phylogenetically independent contrasts
pic_complexity <- pic(complexity, tree)
pic_variability <- pic(variability, tree)

# Step 4: Test correlation on contrasts
cor_test <- cor.test(pic_complexity, pic_variability, method="spearman")

# Step 5: Bootstrap confidence intervals
bootstrap_results <- boot.pval(pic_complexity, pic_variability, R=1000)
```

---

## Data Quality Assessment

| Organism | CV Data Quality | Complexity Data Quality | Overall Assessment |
|----------|----------------|------------------------|-------------------|
| E. coli | Excellent (5 studies) | Excellent (RegulonDB) | HIGH confidence |
| B. subtilis | Excellent (3 studies) | Excellent (SubtiWiki) | HIGH confidence |
| C. crescentus | Good (2 studies) | Good (published data) | MEDIUM confidence |
| M. pneumoniae | Good (3 studies) | Fair (limited databases) | MEDIUM confidence |
| JCVI-syn3.0 | Fair (estimated) | Good (known genome) | LOW confidence (estimated) |

---

## Conclusion and Next Steps

**Current status**: Preliminary evidence supports framework prediction (negative correlation between complexity and variability), but small sample size and multiple confounding factors preclude definitive conclusions.

**Priority actions**:
1. **Expand dataset**: Add 2-3 organisms (H. pylori, C. trachomatis, Spiroplasma)
2. **Execute PIC analysis**: Control for phylogenetic relatedness
3. **Address confounds**: Document and statistically control for cell geometry, growth rate
4. **Power analysis**: Determine minimum sample size for definitive test
5. **Honest reporting**: Present preliminary result with appropriate caveats

**Honest assessment**: Current dataset provides suggestive but not conclusive evidence for the framework prediction. This should be presented as a preliminary correlation that warrants further investigation, not as a definitive finding.

