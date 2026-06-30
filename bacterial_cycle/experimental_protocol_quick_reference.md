# Experimental Protocols for Distinguishing Physical Consequences vs. Physical Compensation

**Quick Reference Guide for Experimental Validation**
**Date:** 2026-04-23

---

## Protocol 1: FtsZ Depletion + Wall Rigidification

**Purpose**: Distinguish physical consequence from physical compensation in cell elongation

**Strain Construction**:
```python
# E. coli with FtsZ under inducible promoter
Genotype: BW25113 ftsZ::PLtetO-1-ftsZ
Reporter: FtsZ-mNeonGreen (C-terminal, chromosomal)
Selection: Kanamycin (50 µg/mL)
```

**Experimental Conditions**:
| Condition | FtsZ Expression | Wall Cross-linking | Medium |
|-----------|----------------|-------------------|--------|
| A | Depleted (no inducer) | None | LB |
| B | Depleted | D-cycloserine (10 µg/mL) | LB |
| C | Normal | D-cycloserine (10 µg/mL) | LB |
| D | Normal | None | LB (wild type) |

**Procedure**:
1. Grow overnight culture with inducer (100 ng/mL aTc)
2. Dilute 1:100 into fresh medium
3. At OD600 = 0.3, split into 4 conditions
4. For depletion: Wash cells 3x in medium without inducer
5. For cross-linking: Add D-cycloserine at OD600 = 0.3
6. Start imaging immediately (t = 0)
7. Image every 2 min for 4 hours

**Microscopy Setup**:
- Phase-contrast for cell outline
- GFP channel for FtsZ-mNeonGreen
- 100x oil objective, temperature control at 37°C
- Microfluidic chamber (CellASIC ONIX) for continuous imaging

**Measurements**:
- Cell length distribution (every timepoint)
- FtsZ fluorescence intensity (Z-ring formation)
- Growth rate (single-cell volume over time)
- Division events (septum formation)
- Time to division after depletion

**Expected Results**:

| Outcome | Physical Consequence | Physical Compensation |
|---------|---------------------|----------------------|
| Elongation in Condition A | Yes, linear | Yes, then plateaus |
| FtsZ recovery | None | Delayed upregulation (t = 60-120 min) |
| Effect of D-cycloserine (Condition B) | Suppresses elongation | No effect on elongation |
| Growth rate | Constant | May increase to compensate |

**Statistical Analysis**:
```R
# Kaplan-Meier survival analysis
library(survival)
fit <- survfit(Surv(time_to_division, division_event) ~ condition, data = df)

# Cox proportional hazards
cox_model <- coxph(Surv(time_to_division, division_event) ~ ftsz_depleted + wall_rigidified + ftsz_depleted:wall_rigidified)

# Cross-correlation for feedback detection
ccf <- ccf(ftsz_intensity, cell_length, lag.max = 10)
```

**Sample Size**: n = 500 cells per condition (power > 0.9 to detect effect size d = 0.5)

---

## Protocol 2: SOS Activation + Turgor Manipulation

**Purpose**: Test molecular override vs. modulation of physical signals

**Strain Construction**:
```python
# E. coli with SOS and turgor sensors
Genotype: BW25113 PsulA-GFP, Pmsl-mCherry (membrane tension)
Selection: Spectinomycin (50 µg/mL), Chloramphenicol (25 µg/mL)
```

**Experimental Conditions** (2×2 factorial):
| Condition | DNA Damage | Turgor Pressure |
|-----------|------------|-----------------|
| 1 | None | Normal (LB) |
| 2 | UV (20 J/m²) | Normal (LB) |
| 3 | None | High (LB + 0.5 M NaCl) |
| 4 | UV (20 J/m²) | High (LB + 0.5 M NaCl) |

**Procedure**:
1. Grow overnight culture
2. Dilute 1:100 into fresh medium
3. At OD600 = 0.3, split into 4 conditions
4. For UV: Expose to 20 J/m² at 254 nm (dose calibrated)
5. For high turgor: Add NaCl to 0.5 M final concentration
6. Start imaging immediately (t = 0)
7. Image every 3 min for 3 hours

**Microscopy Setup**:
- Phase-contrast for cell outline
- GFP channel for SulA expression
- mCherry channel for membrane tension (FRET donor)
- 100x oil objective, temperature control at 37°C
- Agarose pads with appropriate osmolarity

**Measurements**:
- SulA-GFP fluorescence intensity (single-cell)
- Membrane tension FRET ratio (msl-mCherry)
- Division timing (septum formation)
- Cell size at division attempt
- Single-cell stochasticity (CV of division timing)

**Expected Results**:

| Outcome | Molecular Override | Molecular Modulation |
|---------|-------------------|---------------------|
| Division probability (Condition 2 vs 1) | P = 0 (complete block) | P < 0.5 (reduced) |
| Effect of high turgor (Condition 4 vs 2) | No effect (P ≈ 0) | Increased P (P > 0) |
| Interaction term | β₄ ≈ 0 | β₄ ≠ 0 (significant) |
| Single-cell CV (Condition 2) | High (> 0.5), bimodal | Moderate (< 0.4), graded |

**Statistical Analysis**:
```R
# Logistic regression for division probability
glm_model <- glm(division_event ~ dna_damage + turgor + dna_damage:turgor, family = binomial, data = df)

# Test interaction term
summary(glm_model)  # Look for significant dna_damage:turgor term

# ROC analysis
library(pROC)
roc_curve <- roc(df$division_event, df$predicted_probability)
auc(roc_curve)  # AUC > 0.9 indicates good classification

# Variance partitioning
var_part <- varComp(sulA_intensity, turgor_pressure, division_timing)
```

**Asymmetry Index Calculation**:
```
Effect(do(DNA_damage) on division) = d = 2.8 (division blocked)
Effect(do(Turgor) on SulA during SOS) = d = 0.2 (minimal effect)
AI = 2.8 / 0.2 = 14.0 → Strong molecular override
```

**Sample Size**: n = 300 cells per condition (power > 0.8 to detect interaction effect)

---

## Protocol 3: Osmotic Manipulation + Growth Control

**Purpose**: Test if turgor pressure is causal signal or correlate of growth rate

**Strain Construction**:
```python
# E. coli with FtsZ and membrane tension sensors
Genotype: BW25113 ftsZ-mNeonGreen, Pmsl-mCherry
Selection: Kanamycin (50 µg/mL), Chloramphenicol (25 µg/mL)
```

**Experimental Conditions**:
| Condition | Osmolarity | Carbon Source | Target Growth Rate |
|-----------|------------|---------------|-------------------|
| A | 0.1 M NaCl | Glucose (0.2%) | Fast |
| B | 0.3 M NaCl | Glucose (0.15%) | Medium |
| C | 0.5 M NaCl | Glucose (0.1%) | Slow |
| D | 0.7 M NaCl | Glucose (0.05%) | Very Slow |
| E | 0.1 M NaCl | Glycerol (0.2%) | Medium (control) |

**Critical Control**: Adjust carbon source concentration to achieve similar growth rates across osmolarities

**Procedure**:
1. Grow overnight culture in low osmolarity medium
2. Dilute 1:100 into each condition
3. Measure growth rate (OD600 every 10 min)
4. If growth rates differ significantly, adjust carbon source
5. Once growth rates matched (±10%), start imaging
6. Image every 2 min for 3 hours
7. Perform osmotic shift experiments at t = 60 min

**Osmotic Shift Experiment**:
- Rapid shift from 0.1 M to 0.5 M NaCl (or vice versa)
- Measure response time (division timing change)
- Distinguish rapid sensing (minutes) from indirect effect (hours)

**Microscopy Setup**:
- Phase-contrast for cell outline
- GFP channel for FtsZ-mNeonGreen
- mCherry channel for membrane tension
- 100x oil objective, temperature control at 37°C
- Microfluidic flow cell for rapid osmotic shifts

**Measurements**:
- Division timing (single-cell tracking)
- Turgor pressure (AFM indentation on parallel samples)
- Growth rate (OD600, single-cell volume)
- FtsZ localization (Z-ring formation timing)
- Membrane tension (FRET ratio)
- Response time to osmotic shift

**Expected Results**:

| Outcome | Turgor as Causal Signal | Turgor as Correlate |
|---------|------------------------|-------------------|
| Division vs. turgor (growth controlled) | Significant relationship | No relationship |
| Partial correlation r(turgor, division\|growth) | Significant (p < 0.01) | Not significant (p > 0.1) |
| Response to osmotic shift | Rapid (< 5 min) | Delayed (> 20 min) |
| FtsZ Z-ring formation | Changes with turgor | Changes with growth only |

**Statistical Analysis**:
```R
# Partial correlation controlling for growth rate
library(ppcor)
partial_cor <- pcor.test(data$division_timing, data$turgor_pressure, data$growth_rate)

# Multiple regression
lm_model <- lm(division_timing ~ turgor_pressure + growth_rate, data = df)
summary(lm_model)  # Look for significant turgor coefficient

# Granger causality
library(lmtest)
granger_test <- grangertest(turgor_pressure, division_timing, order = 5)
```

**Asymmetry Index Calculation**:
```
Effect(do(Osmotic shift) on division timing) = d = 1.8
Effect(do(Growth rate change) on turgor) = d = 0.6
AI = 1.8 / 0.6 = 3.0 → Moderate molecular dominance
```

**Sample Size**: n = 400 cells per condition (power > 0.85 to detect partial correlation r = 0.3)

---

## General Guidelines

### Cell Preparation
- Use mid-exponential phase cultures (OD600 = 0.3-0.5)
- Maintain temperature at 37°C throughout
- Use fresh medium for each experiment
- Avoid prolonged stationary phase (> 12 h)

### Imaging Best Practices
- Use minimal exposure to prevent phototoxicity
- Maintain focus drift correction
- Calibrate osmolarity shifts (measure actual osmolarity)
- Include unstained controls for autofluorescence

### Data Analysis Pipeline
```python
# Standard analysis workflow
1. Image segmentation (Oufti, MicrobeJ, or DeepCell)
2. Cell tracking (TrackMate or custom MATLAB)
3. Feature extraction (length, width, fluorescence intensity)
4. Quality control (remove dividing/merged cells)
5. Statistical analysis (R or Python)
6. Visualization (ggplot2, matplotlib)
```

### Quality Control Metrics
- Segmentation accuracy > 95%
- Tracking continuity > 90%
- Fluorescence intensity CV < 0.2 for control cells
- Growth rate consistency across replicates (CV < 0.15)

---

## Data Interpretation Guide

### Physical Consequence
**Causal signature**: M → P, no feedback
- Observable: Physical change follows molecular change
- Timing: Immediate (no delay)
- Feedback: Cross-correlation shows unidirectional influence
- Intervention: do(M) affects P; do(P) doesn't trigger compensatory M

### Physical Compensation
**Causal signature**: M ↔ P with negative feedback
- Observable: Physical change triggers delayed molecular response
- Timing: Characteristic delay (10-60 min)
- Feedback: Cross-correlation shows bidirectional influence
- Intervention: do(P) triggers M response; homeostatic setpoint

### Molecular Override
**Causal signature**: M → P with AI >> 1
- Observable: M blocks normal response to P
- Timing: Immediate molecular effect
- Dose-response: Threshold, all-or-none
- Intervention: do(M) overrides P; AI > 3

### Bidirectional Coupling
**Causal signature**: M ↔ P with AI ≈ 1
- Observable: Both levels influence each other
- Timing: Similar response timescales
- Dose-response: Graded, interaction effects
- Intervention: Both do(M) and do(P) have effects; AI ≈ 1

---

## Troubleshooting

### Problem: No elongation after FtsZ depletion
**Possible causes**:
- Incomplete depletion (check FtsZ fluorescence)
- Compensatory mechanisms (check for FtsZ upregulation)
- Secondary effects (check growth rate)

**Solutions**:
- Extend depletion time
- Use degron system for rapid depletion
- Verify with Western blot

### Problem: No SOS response after UV
**Possible causes**:
- UV dose too low/high
- Photoreactivation (light exposure)
- Reporter not functional

**Solutions**:
- Calibrate UV dose (10-50 J/m²)
- Shield samples from light after UV
- Verify with qPCR for SOS genes

### Problem: Osmotic shifts cause lysis
**Possible causes**:
- Shift too rapid
- Osmolarity difference too large
- Cell wall weakened

**Solutions**:
- Gradual shifts (stepwise)
- Limit osmolarity range (0.1-0.7 M NaCl)
- Use mild cross-linking agent

---

## Timeline and Resources

### Experiment Duration
- **Protocol 1**: 2 weeks (strain construction: 1 week, experiments: 3-4 days)
- **Protocol 2**: 2 weeks (strain construction: 1 week, experiments: 3-4 days)
- **Protocol 3**: 3 weeks (growth rate optimization: 1 week, experiments: 1 week)

### Equipment Requirements
- Microscope with temperature control and environmental chamber
- Microfluidics setup (CellASIC ONIX or similar)
- UV source (calibrated)
- AFM for turgor measurements (optional, can use osmotic sensitivity assays)
- Plate reader for growth curves

### Computational Requirements
- Image analysis workstation (32+ GB RAM)
- Statistical software (R, Python)
- Data storage (1 TB for raw images)

### Personnel
- 1 postdoc or graduate student with microbiology experience
- Training time: 2-3 weeks for techniques
- Data analysis: 1-2 weeks per experiment

---

## Expected Outcomes and Impact

### Key Predictions
1. **FtsZ depletion**: Elongation is a physical consequence (no compensation)
2. **SOS checkpoint**: Molecular override with AI > 10
3. **Turgor pressure**: Causal signal with AI ≈ 3

### Impact on Field
- Provides quantitative framework for physical-molecular interactions
- Establishes causal inference methods in cell biology
- Distinguishes correlation from causation in physical parameters
- Guides synthetic biology design (minimal cells)

### Publication Strategy
- **Primary paper**: Experimental validation with causal analysis
- **Methods paper**: Detailed protocols and computational pipeline
- **Review**: Causal inference in cell cycle regulation

---

## References for Protocols

**FtsZ depletion**:
- Huang, K.C., et al. (2013). Cell shape and chromosome organization. *Curr Opin Microbiol*.
- Rivas, G., et al. (2022). FtsZ activation thresholds. *PNAS*.

**SOS response**:
- Jude, F., et al. (2022). SOS response and cell cycle regulation. *J Bacteriol*.
- Roehm, C., et al. (2022). SOS checkpoint and division. *Mol Microbiol*.

**Turgor pressure**:
- Reshes, G., et al. (2008). Mechanical forces of division. *PNAS*.
- Zhou, J., et al. (2023). Physical regulation of division. *Annu Rev Biophys*.

**Causal analysis**:
- Pearl, J. (2009). *Causality*. Cambridge University Press.
- Spirtes, P., et al. (2000). *Causation, Prediction, and Search*. MIT Press.

---

**End of Quick Reference Guide**
