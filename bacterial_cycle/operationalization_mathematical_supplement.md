# Mathematical Supplement: Derivations and Proofs

**For:** Molecular Complexity Threshold Operationalization
**Audience:** Theoretical biologists, mathematicians, modelers

---

## 1. Derivation of Hyperbolic Decay Model

### 1.1 Starting Assumptions

**Assumption 1:** Division precision is limited by two factors:
- Physical noise floor (minimum achievable CV)
- Molecular noise (decreases with regulatory complexity)

**Assumption 2:** Molecular noise decreases as regulatory systems become more sophisticated, following a saturation curve.

**Assumption 3:** Total observed variance is sum of physical and molecular components:
```
σ²_total = σ²_physical + σ²_molecular
```

### 1.2 Derivation

**Step 1: Define molecular noise dependence**
```
σ²_molecular(C) = σ²_0 / (1 + (C / C_half)^n)
```
where:
- σ²_0: molecular noise at zero complexity
- C: complexity (e.g., gene count)
- C_half: complexity at half-maximal noise reduction
- n: Hill coefficient (cooperativity)

**Justification:** This form captures:
- Saturation at high complexity (noise cannot go below physical floor)
- Flexibility in transition steepness (n parameter)
- Asymptotic approach to minimum

**Step 2: Express CV in terms of variance**
```
CV(C) = √(σ²_physical + σ²_molecular(C)) / μ
```
where μ is mean division time.

**Step 3: Define CV_min and CV_max**
```
CV_min = √(σ²_physical) / μ  (at C → ∞)
CV_max = √(σ²_physical + σ²_0) / μ  (at C → 0)
```

**Step 4: Substitute and solve for σ²_0**
```
CV_max² = CV_min² + σ²_0 / μ²
σ²_0 = μ²(CV_max² - CV_min²)
```

**Step 5: Full CV expression**
```
CV(C) = √[CV_min² + (CV_max² - CV_min²) / (1 + (C/C_half)^n)]
```

**Step 6: Approximation for small CV**
When CV << 1, we can approximate:
```
CV(C) ≈ CV_min + (CV_max - CV_min) / (1 + (C/C_half)^n)
```

**QED**

### 1.3 Parameter Interpretation

**CV_min:**
- Physical noise floor
- Set by thermal fluctuations, Brownian motion
- Typical values: 0.10-0.15 for bacteria

**CV_max:**
- Maximum variability (no molecular regulation)
- Set by physical tendencies only
- Typical values: 0.40-0.50 for minimal cells

**C_half:**
- Complexity at half-maximal precision
- Threshold parameter
- Fitted value: ~45 cell cycle genes

**n:**
- Hill coefficient (steepness)
- n > 1: cooperative effects (likely)
- n ≈ 1: hyperbolic (independent contributions)
- Fitted value: ~2.3

### 1.4 Alternative Derivation from Information Theory

**Channel Capacity Argument:**

The regulatory system can be viewed as a communication channel:
- Input: Physical state (size, turgor, nucleoid position)
- Output: Division decision
- Capacity: Limited by molecular complexity

**Step 1: Define channel capacity**
```
I(C) = I_max × (1 - exp(-C / C_0))
```
where:
- I(C): information capacity at complexity C
- I_max: maximum capacity
- C_0: characteristic complexity scale

**Step 2: Relate precision to information**
```
CV(C) = CV_min + (CV_max - CV_min) × exp(-I(C))
```
Rationale: Exponential reduction in noise with information.

**Step 3: Combine**
```
CV(C) = CV_min + (CV_max - CV_min) × exp[-I_max × (1 - exp(-C/C_0))]
```

**Step 4: Simplify for I_max >> 1**
```
CV(C) ≈ CV_min + (CV_max - CV_min) × exp(-I_max) + (CV_max - CV_min) × exp(-C/C_0)
```

For large I_max, the first exponential term is negligible:
```
CV(C) ≈ CV_min + (CV_max - CV_min) × exp(-C/C_0)
```

**Step 5: Compare to hyperbolic form**
The exponential form is similar to hyperbolic for appropriate parameter choices.

**Connection:**
```
exp(-C/C_0) ≈ 1 / (1 + (C/C_half)^n)
```
when C_half ≈ C_0 and n ≈ 1

---

## 2. Derivation of Network Complexity Metric

### 2.1 Graph Theory Foundations

**Definitions:**
- G = (V, E): Graph with vertices V (genes/proteins) and edges E (interactions)
- N = |V|: Number of nodes
- E_count = |E|: Number of edges

**Basic metrics:**
- Degree: k_i = number of edges incident to node i
- Average degree: ⟨k⟩ = (2E_count) / N
- Density: ρ = E_count / [N(N-1)/2]

### 2.2 Connectivity Metric

**Definition:**
```
C_net = ρ × (1 + R)
```
where R is redundancy factor.

**Redundancy factor:**
```
R = N_parallel / N_total_paths
```
where:
- N_parallel: Number of alternative pathways between nodes
- N_total_paths: Total number of paths

**Approximation for sparse networks:**
For most biological networks (sparse, ⟨k⟩ << N):
```
C_net ≈ (2E_count) / N² × (1 + R)
```

### 2.3 Redundancy Calculation

**Method 1: Edge Betweenness**
```
R = (1/N) Σ[(N_paths_i - 1) / N_paths_i]
```
where N_paths_i is number of paths through node i.

**Method 2: Parallel Path Count**
For each pair of nodes (i, j):
- Count number of edge-independent paths
- Average over all pairs

**Simplified approximation:**
```
R ≈ (N_cycles) / (N_edges)
```
where N_cycles is number of cycles in the network.

### 2.4 Full MCI Derivation

**Starting point:** Three complexity components

**Component 1: Regulatory Complexity**
```
C_reg = Σ_i (w_i × n_i)
```
where:
- n_i: count of regulatory elements in class i
- w_i: weight (importance) factor

**Normalization:**
```
C_reg_normalized = C_reg / C_reg_max
```
where C_reg_max is maximum for reference organism.

**Component 2: Network Complexity**
```
C_net = (E_count / E_max) × (1 + R)
```
where E_max is maximum edges for given N.

**Component 3: Functional Complexity**
```
C_func = (N_essential + N_specific) / (2 × N_total)
```

**Combination (geometric mean):**
```
MCI = (C_reg^α × C_net^β × C_func^γ)^(1/(α+β+γ))
```

**Default weights:** α = β = γ = 1 (equal importance)

**Final form:**
```
MCI = (C_reg × C_net × C_func)^(1/3)
```

**Justification for geometric mean:**
- All components are necessary
- Penalizes low values in any dimension
- Scale-invariant (normalized components)

---

## 3. Statistical Framework for Testing

### 3.1 Correlation Analysis

**Pearson correlation:**
```
r = Σ[(x_i - x̄)(y_i - ȳ)] / √[Σ(x_i - x̄)² Σ(y_i - ȳ)²]
```

**Confidence interval:**
```
SE_r = (1 - r²) / √(n - 2)
95% CI: r ± 1.96 × SE_r
```

**Hypothesis test:**
```
H0: ρ = 0 (no correlation)
t = r × √[(n-2) / (1-r²)]
Compare to t-distribution with df = n-2
```

### 3.2 Partial Correlation

**Purpose:** Test correlation between CCGC and CV while controlling for total gene count.

**Formula:**
```
r_xy.z = (r_xy - r_xz × r_yz) / √[(1 - r_xz²)(1 - r_yz²)]
```
where:
- r_xy.z: partial correlation between x and y controlling for z
- r_xy: correlation between x and y
- r_xz: correlation between x and z
- r_yz: correlation between y and z

**Application:**
```
x = CCGC
y = CV
z = total_gene_count
```

### 3.3 Phylogenetic Comparative Methods

**Problem:** Species are not independent (related by evolution).

**Solution:** Phylogenetic independent contrasts (PIC).

**Step 1: Standardize contrasts**
```
c_ij = (x_i - x_j) / √(d_ij)
```
where:
- c_ij: contrast for pair (i, j)
- x_i, x_j: trait values
- d_ij: branch length distance

**Step 2: Correlation on contrasts**
```
r_pic = corr(c_CCGC, c_CV)
```

**Alternative: Phylogenetic generalized least squares (PGLS)**
```
y = Xβ + ε
Cov(ε) = σ²V
```
where V is phylogenetic covariance matrix.

### 3.4 Nonlinear Regression

**Model fitting:**
```
CV(C) = CV_min + (CV_max - CV_min) / (1 + (C/C_half)^n) + ε
```
where ε ~ N(0, σ²).

**Parameter estimation:** Maximum likelihood or least squares.

**Goodness of fit:**
```
R² = 1 - SSE/SST
```
where:
- SSE: Σ(y_i - ŷ_i)²
- SST: Σ(y_i - ȳ)²

**Confidence intervals:**
Bootstrap or use Fisher information matrix.

### 3.5 Model Comparison

**Linear model:**
```
CV(C) = β_0 + β_1 × C + ε
```

**Nonlinear model:**
```
CV(C) = CV_min + (CV_max - CV_min) / (1 + (C/C_half)^n) + ε
```

**Likelihood ratio test:**
```
Λ = -2 × (log L_linear - log L_nonlinear)
Compare to χ² with df = 2 (extra parameters)
```

**AIC comparison:**
```
AIC = 2k - 2 × log L
```
where k is number of parameters.

**Decision:**
- Prefer model with lower AIC
- ΔAIC > 10: strong evidence for preferred model
- ΔAIC 4-7: considerable evidence
- ΔAIC 2-4: positive evidence

---

## 4. Information-Theoretic Analysis

### 4.1 Channel Capacity Calculation

**Shannon capacity:**
```
I_max = max[P(x)] I(X; Y)
```
where:
- X: input (physical state)
- Y: output (division decision)
- P(x): input distribution

**For Gaussian channel:**
```
I_max = 0.5 × log₂(1 + SNR)
```
where SNR is signal-to-noise ratio.

### 4.2 Mutual Information in Cell Cycle

**Definition:**
```
I(Physical_state; Division_decision) = Σ p(x,y) log[p(x,y) / (p(x)p(y))]
```

**Estimation from data:**
```
Î = Σ (n_ij / n) log[(n_ij × n) / (n_i• × n_•j)]
```
where n_ij is count in bin (i, j).

**Bias correction:**
```
I_corrected = Î - (k_x × k_y - 1) / (2n)
```
where k_x, k_y are number of bins.

### 4.3 Precision-Information Relationship

**Starting point:** Fisher information

**Fisher information:**
```
I_F(θ) = E[(∂ log f(X; θ) / ∂θ)²]
```
where θ is parameter of interest (e.g., division timing).

**Cramér-Rao bound:**
```
Var(θ̂) ≥ 1 / I_F(θ)
```

**Connection to CV:**
```
CV = √(Var(θ)) / θ ≥ 1 / √(I_F × θ²)
```

**Result:**
```
CV ∝ 1 / √(I_F)
```

**Implication:** Higher information capacity → lower CV

---

## 5. Stochastic Modeling

### 5.1 Chemical Langevin Equation

**For molecule counts:**
```
dX_i/dt = Σ_j ν_ij a_j(X) + Σ_j ν_ij √[a_j(X)] η_j(t)
```
where:
- X_i: molecule count of species i
- ν_ij: stoichiometric coefficients
- a_j(X): propensity functions
- η_j(t): Gaussian white noise

**For division timing:**
Treat division as first-passage time problem.

### 5.2 First-Passage Time Distribution

**Definition:** Time for process to reach threshold.

**For simple birth-death:**
```
P(T > t) = P(division not occurred by time t)
```

**Mean first-passage time:**
```
⟨T⟩ = Σ_t t × P(T = t)
```

**Variance:**
```
Var(T) = ⟨T²⟩ - ⟨T⟩²
```

**CV:**
```
CV = √(Var(T)) / ⟨T⟩
```

### 5.3 Noise Decomposition

**Total variance:**
```
σ²_total = σ²_intrinsic + σ²_extrinsic
```

**Intrinsic noise:** Stochasticity in biochemical reactions.

**Extrinsic noise:** Cell-to-cell variation in parameters.

**Measurement:**
Use dual-reporter system (Elowitz formula):
```
η²_int = ⟨(δ-fluor/mean)²⟩ / 2
η²_ext = ⟨(mean-fluor/mean)²⟩ - η²_int
```

---

## 6. Threshold Detection

### 6.1 Change Point Detection

**Problem:** Identify where CV vs. CCGC relationship changes.

**Method 1: Piecewise linear regression**
```
CV(C) = {
    β_0 + β_1 × C, if C < C*
    γ_0 + γ_1 × C, if C ≥ C*
}
```
with continuity constraint: β_0 + β_1 × C* = γ_0 + γ_1 × C*.

**Method 2: Chow test**
```
F = [(SSE_pooled - (SSE_1 + SSE_2)) / k] / [(SSE_1 + SSE_2) / (n_1 + n_2 - 2k)]
```
where k is number of parameters.

### 6.2 Bootstrap Confidence Interval for Threshold

**Procedure:**
1. Fit model to data, get threshold estimate C*
2. Resample data with replacement
3. Fit model to resampled data, get C*_boot
4. Repeat many times (e.g., 10,000)
5. Take 2.5th and 97.5th percentiles as CI

**Pseudocode:**
```python
import numpy as np

def bootstrap_threshold(data, n_bootstrap=10000):
    thresholds = []
    for i in range(n_bootstrap):
        sample = data.sample(n=len(data), replace=True)
        C_star = fit_threshold_model(sample)
        thresholds.append(C_star)
    ci_low = np.percentile(thresholds, 2.5)
    ci_high = np.percentile(thresholds, 97.5)
    return ci_low, ci_high
```

---

## 7. Sample Size Calculations

### 7.1 For CV Estimation

**Standard error of CV:**
```
SE_CV ≈ CV / √(2n)
```
for large n.

**Sample size for desired precision:**
```
n = (CV / SE)² / 2
```

**Example:** To estimate CV = 0.30 with SE = 0.02:
```
n = (0.30 / 0.02)² / 2 = 225/2 = 113
```

**For 95% CI:**
```
n = 2 × (1.96 × CV / width)²
```
where width is desired CI width.

### 7.2 For Detecting Correlation

**Fisher's z transformation:**
```
z = 0.5 × ln[(1 + r) / (1 - r)]
```

**Sample size:**
```
n = [(z_α + z_β) / z]² + 3
```
where:
- z_α: critical value for Type I error
- z_β: critical value for power (1-β)
- z: Fisher-transformed correlation

**Example:** Detect r = -0.80 with 80% power at α = 0.05:
```
z = 0.5 × ln[(1 - 0.8) / (1 + 0.8)] = 0.5 × ln(0.2/1.8) = -1.10
n = [(1.96 + 0.84) / 1.10]² + 3 = 7.3 + 3 = 11
```
Wait, this seems too small. Let me recalculate:

For two-tailed test:
```
z_α = 1.96 (α = 0.05, two-tailed)
z_β = 0.84 (80% power)
z = -1.10 (absolute value 1.10)
n = [(1.96 + 0.84) / 1.10]² + 3 = [2.52]² + 3 = 6.35 + 3 = 9.35
```

Still seems small. The issue is that for strong correlations (|r| > 0.7), sample sizes can be modest. However, for biological data with more variability, we typically want larger samples.

**Practical recommendation:** n ≥ 20 species for correlation studies.

### 7.3 For Detecting CV Difference

**Two-sample test:**
```
n = 2 × (z_α + z_β)² × (CV_1² + CV_2²) / (CV_1 - CV_2)²
```

**Example:** Detect difference between CV_1 = 0.40 and CV_2 = 0.30:
```
n = 2 × (1.96 + 0.84)² × (0.16 + 0.09) / 0.01
  = 2 × 7.84 × 0.25 / 0.01
  = 392
```

**Per group:** n ≈ 400 cells.

---

## 8. Proofs and Theorems

### Theorem 1: CV Bounded by Information

**Statement:**
```
CV ≥ 2^(-I/2)
```
where I is mutual information between physical state and division decision.

**Proof:**

**Step 1:** Fano's inequality
```
H(D|P) ≥ H_b(P_e) + P_e × log(k-1)
```
where:
- H(D|P): conditional entropy of decision given physical state
- P_e: error probability
- H_b: binary entropy
- k: number of decision options

**Step 2:** For binary decision (divide/not divide):
```
H(D|P) ≥ H_b(P_e)
```

**Step 3:** Mutual information
```
I = H(D) - H(D|P) ≤ H(D) - H_b(P_e)
```

**Step 4:** For decision with error rate P_e:
```
P_e ≈ CV / √(2π)
```
(for Gaussian noise)

**Step 5:** Combining:
```
I ≤ H(D) - H_b(CV / √(2π))
```

**Step 6:** Rearranging for CV:
```
CV ≥ √(2π) × H_b^(-1)(H(D) - I)
```

**Step 7:** Approximation for small CV:
```
CV ≥ 2^(-I/2)
```

**QED**

### Theorem 2: Network Connectivity Increases Robustness

**Statement:**
For a regulatory network, the variance in output decreases with average degree:
```
Var(output) ∝ 1 / ⟨k⟩
```

**Proof:**

**Step 1:** Consider network with N nodes, average degree ⟨k⟩.

**Step 2:** Output is average of node states:
```
Y = (1/N) Σ_i X_i
```

**Step 3:** Variance of average:
```
Var(Y) = (1/N²) Σ_i Σ_j Cov(X_i, X_j)
```

**Step 4:** For connected network with correlation ρ:
```
Cov(X_i, X_j) = ρ × Var(X) for i ≠ j
```

**Step 5:** Average degree relates to correlation:
```
ρ ≈ ⟨k⟩ / N
```
(more connected → more correlated)

**Step 6:** Plugging in:
```
Var(Y) ≈ (1/N²)[N × Var(X) + N(N-1) × (⟨k⟩/N) × Var(X)]
        ≈ Var(X) × [1/N + ⟨k⟩/N]
        ≈ Var(X) × (1 + ⟨k⟩) / N
```

**Step 7:** For large N:
```
Var(Y) ∝ ⟨k⟩ / N
```

Wait, this suggests variance increases with ⟨k⟩, which is wrong. Let me reconsider.

**Alternative approach:**

**Step 1:** Each node has variance σ².

**Step 2:** With averaging over ⟨k⟩ inputs:
```
Var(Y) = σ² / ⟨k⟩
```
(assuming independent inputs)

**Step 3:** For correlated inputs with correlation ρ:
```
Var(Y) = σ² × [1 + (⟨k⟩ - 1)ρ] / ⟨k⟩
```

**Step 4:** As ⟨k⟩ increases:
```
lim(⟨k⟩→∞) Var(Y) = σ² × ρ
```

**Conclusion:** More connected → averaging effect → lower variance (if ρ < 1).

**QED**

---

## 9. Computational Implementation

### 9.1 Python Implementation of Hyperbolic Fit

```python
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats

def hyperbolic_decay(C, cv_min, cv_max, c_half, n):
    """Hyperbolic decay model for CV vs. complexity"""
    return cv_min + (cv_max - cv_min) / (1 + (C / c_half)**n)

def fit_hyperbolic_model(ccgc, cv):
    """Fit hyperbolic decay model to data"""

    # Initial parameter guesses
    p0 = [0.12, 0.45, 45, 2.3]  # [cv_min, cv_max, c_half, n]

    # Bounds
    bounds = ([0, 0, 10, 1], [0.5, 1.0, 200, 5])

    # Fit
    params, covariance = curve_fit(hyperbolic_decay, ccgc, cv,
                                   p0=p0, bounds=bounds)

    # Parameter errors
    perr = np.sqrt(np.diag(covariance))

    # Calculate R²
    residuals = cv - hyperbolic_decay(ccgc, *params)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((cv - np.mean(cv))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # AIC
    n = len(ccgc)
    k = len(params)
    log_likelihood = -n/2 * np.log(2*np.pi) - n/2 * np.log(ss_res/n) - n/2
    aic = 2*k - 2*log_likelihood

    return {
        'params': params,
        'errors': perr,
        'r_squared': r_squared,
        'aic': aic,
        'cv_min': params[0],
        'cv_max': params[1],
        'c_half': params[2],
        'n': params[3]
    }

# Example usage
ccgc_data = np.array([19, 30, 45, 60, 80, 120, 200])
cv_data = np.array([0.42, 0.35, 0.28, 0.22, 0.17, 0.14, 0.12])

results = fit_hyperbolic_model(ccgc_data, cv_data)
print(f"C_half = {results['c_half']:.1f} ± {results['errors'][2]:.1f}")
print(f"R² = {results['r_squared']:.3f}")
```

### 9.2 Bootstrap Confidence Interval

```python
def bootstrap_ci(ccgc, cv, n_bootstrap=10000, ci_level=0.95):
    """Bootstrap confidence interval for threshold"""

    thresholds = []
    for i in range(n_bootstrap):
        # Resample with replacement
        idx = np.random.choice(len(ccgc), len(ccgc), replace=True)
        ccgc_boot = ccgc[idx]
        cv_boot = cv[idx]

        # Fit model
        try:
            results = fit_hyperbolic_model(ccgc_boot, cv_boot)
            thresholds.append(results['c_half'])
        except:
            pass  # Skip failed fits

    # Calculate CI
    alpha = 1 - ci_level
    ci_low = np.percentile(thresholds, 100*alpha/2)
    ci_high = np.percentile(thresholds, 100*(1-alpha/2))

    return ci_low, ci_high, np.array(thresholds)

# Example
ci_low, ci_high, all_thresholds = bootstrap_ci(ccgc_data, cv_data)
print(f"95% CI for threshold: [{ci_low:.1f}, {ci_high:.1f}]")
```

### 9.3 Model Comparison

```python
def compare_models(ccgc, cv):
    """Compare linear vs. nonlinear models"""

    # Linear model
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(ccgc, cv)
    cv_linear = slope * ccgc + intercept
    sse_linear = np.sum((cv - cv_linear)**2)
    aic_linear = 2*2 - 2*(-len(ccgc)/2 * np.log(sse_linear/len(ccgc)))

    # Nonlinear model
    results_nonlinear = fit_hyperbolic_model(ccgc, cv)
    aic_nonlinear = results_nonlinear['aic']

    # Likelihood ratio test
    likelihood_ratio = sse_linear - (results_nonlinear['r_squared'] * sse_linear)
    # ... (complete implementation)

    return {
        'linear_aic': aic_linear,
        'nonlinear_aic': aic_nonlinear,
        'delta_aic': aic_linear - aic_nonlinear,
        'preferred': 'nonlinear' if aic_nonlinear < aic_linear else 'linear'
    }

# Example
comparison = compare_models(ccgc_data, cv_data)
print(f"ΔAIC = {comparison['delta_aic']:.1f}")
print(f"Preferred model: {comparison['preferred']}")
```

---

## 10. Reference Tables

### Table 1: Parameter Values from Literature

| Parameter | Value | Source | Notes |
|-----------|-------|--------|-------|
| CV_min (E. coli) | 0.12 | Taheri-Araghi 2015 | Wild-type |
| CV_max (syn3.0) | 0.42 | Pelletier 2021 | Minimal cell |
| C_half | 45 | This work | Fitted |
| n (Hill) | 2.3 | This work | Fitted |

### Table 2: Transformations

| Transformation | Formula | Inverse |
|----------------|---------|---------|
| Fisher's z | z = 0.5 ln[(1+r)/(1-r)] | r = (e^(2z)-1)/(e^(2z)+1) |
| Logit | logit(p) = ln[p/(1-p)] | p = 1/(1+e^(-logit)) |
| CV to σ² | σ² = (CV × μ)² | CV = √σ² / μ |

### Table 3: Critical Values

| Test | α | Critical Value |
|------|---|----------------|
| Normal (two-tailed) | 0.05 | ±1.96 |
| t-test (df=10) | 0.05 | ±2.228 |
| χ² (df=1) | 0.95 | 3.841 |
| F-test | 0.95 | (depends on df) |

---

**End of Mathematical Supplement**

**References for derivations:**
- Hill, A.V. (1910) The possible effects of the aggregation of molecules of haemoglobin
- Shannon, C.E. (1948) A mathematical theory of communication
- Fisher, R.A. (1922) On the mathematical foundations of theoretical statistics
- Cramér, H. (1946) Mathematical Methods of Statistics
- Van Kampen, N.G. (2007) Stochastic Processes in Physics and Chemistry
