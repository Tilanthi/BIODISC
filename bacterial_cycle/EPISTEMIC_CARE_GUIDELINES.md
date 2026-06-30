# Epistemic Care Guidelines for Manuscript Revision

**Date:** 2026-04-23
**Purpose:** Ensure all claims in the manuscript distinguish clearly between established mechanisms, correlations, and speculative hypotheses

---

## Principles of Epistemic Care in Biological Writing

### 1. Distinguish Three Levels of Evidence

**Established Mechanisms (Well-Supported)**
- Direct experimental evidence for causation
- Mutational analysis showing necessity
- Reconstitution showing sufficiency
- Consensus in the field
- **Language to use:** "is required for," "establishes," "creates," "determines"

**Correlations (Observed but Mechanism Unclear)**
- Consistent spatial/temporal patterns
- Perturbation affects outcome
- Mechanistic pathway unknown
- Field has not reached consensus
- **Language to use:** "correlates with," "is associated with," "influences," "affects"

**Speculative Hypotheses (Not Established)**
- Theoretical proposals
- Preliminary observations
- Controversial interpretations
- Alternative explanations viable
- **Language to use:** "may contribute to," "has been proposed to," "one hypothesis is that"

---

### 2. Specific Patterns to Watch

**Pattern 1: Localization ≠ Sensing**

**Problematic:** "Protein X localizes to curved membranes, suggesting it senses curvature"
**Better:** "Protein X localizes to curved membranes (Smith et al., 2020). Whether this represents active curvature sensing versus passive accumulation remains unclear."

**Why:** Localization to a physical feature does not establish that the protein detects that feature. It could localize due to other properties (oligomerization, lipid interactions, protein-protein interactions).

---

**Pattern 2: Perturbation Effects ≠ Mechanism**

**Problematic:** "Disrupting membrane curvature affects division, showing curvature sensing"
**Better:** "Disrupting membrane curvature affects division (Jones et al., 2021), but the mechanistic pathway linking curvature to division control is unknown."

**Why:** Perturbation effects show that a parameter matters, but not HOW it is detected or transduced.

---

**Pattern 3: Correlation ≠ Causation**

**Problematic:** "Metabolic state correlates with division timing, indicating metabolic regulation"
**Better:** "Metabolic state correlates with division timing (Lee et al., 2019). Whether this represents direct metabolic regulation versus correlation with other cellular parameters is unclear."

**Why:** Correlation can arise from common causes, bidirectional relationships, or third variables.

---

### 3. Section-by-Section Analysis

#### Section 2.1: Turgor Pressure

**Current claims:**
- "Turgor pressure could contribute to size sensing"
- "FtsZ mechanosensitivity"

**Epistemic status:**
- Correlational: Cell size relates to turgor pressure
- Speculative: Turgor as size sensor
- Mixed: FtsZ responds to tension in vitro, in vivo relevance uncertain

**Recommendation:**
- Add explicit caveats about correlative nature of turgor-size relationship
- Distinguish in vitro FtsZ mechanosensitivity from in vivo relevance

---

#### Section 2.2: Nucleoid Occlusion

**Current claims:**
- SlmA/Noc as molecular implementations of geometric constraint

**Epistemic status:**
- Established: SlmA/Noc prevent division over nucleoid
- Established: Geometric constraint is real
- Established: Molecular mechanisms translate geometry to inhibition

**Assessment:** This section is good - it clearly distinguishes physical constraint from molecular implementation.

---

#### Section 2.3: DNA Supercoiling

**Current claims:**
- Supercoiling affects replication initiation
- Bidirectional coupling

**Epistemic status:**
- Established: DnaA binding is topology-sensitive
- Established: Topoisomerase mutants have replication defects
- Established: Bidirectional relationship

**Assessment:** This section is good - emphasizes bidirectional coupling clearly.

---

#### Section 2.4: Macromolecular Crowding

**Current claims:**
- Phase separation in bacteria
- Crowding affects cell cycle

**Epistemic status:**
- Established: Cytoplasm is crowded
- Speculative: Phase separation in bacteria (controversial)
- Speculative: Crowding thresholds regulate division

**Recommendation:**
- Add stronger caveats about bacterial phase separation controversy
- Clarify that crowding effects on cell cycle are speculative

---

#### Section 2.5: Entropic Forces

**Current claims:**
- Entropic forces drive segregation
- SMC complexes redirect these forces

**Epistemic status:**
- Established: Entropic forces affect chromosome behavior
- Established: SMC complexes are required for proper segregation
- Active debate: How much of segregation can be explained by entropy alone

**Assessment:** This section is good - acknowledges ongoing debate and presents balanced view.

---

#### Section 4.1: Caulobacter (Main Focus)

**Current issues:**
- Physical aspects section conflates correlation with mechanism
- "Sensing" language used without established mechanisms

**Epistemic status:**
- Established: Molecular phosphorelay controls asymmetry
- Established: Physical correlations exist
- Speculative: Physical sensing mechanisms

**Recommendation:** See detailed revision in CAULOBACTER_SECTION_4_1_REVISED.md

---

#### Section 4.2: SOS Checkpoint

**Current claims:**
- Molecular checkpoint overrides physical signals

**Epistemic status:**
- Established: SulA inhibits FtsZ
- Established: Division blocked despite physical permissive conditions
- Well-supported example of molecular override

**Assessment:** This section is good - clearly establishes molecular dominance.

---

#### Section 4.3: Multifork Replication

**Current claims:**
- Molecular precision beyond physical limits

**Epistemic status:**
- Established: Multifork replication occurs
- Established: DnaA-ATP/ADP cycling controls timing
- Well-supported example of molecular sophistication

**Assessment:** This section is good.

---

### 4. Language Quick Reference

#### For Correlations
Use: "correlates with," "is associated with," "co-occurs with," "spatially overlaps with"
Avoid: "due to," "driven by," "caused by"

#### For Speculative Mechanisms
Use: "may contribute to," "has been proposed to," "one hypothesis is that," "remains unclear"
Avoid: "demonstrates that," "shows that," "proves that"

#### For Established Mechanisms
Use: "is required for," "establishes," "creates," "determines," "necessary and sufficient"
Avoid: Nothing - these terms are appropriate for well-established mechanisms

#### For Uncertainty
Use: "remains unclear," "is not yet established," "requires further investigation," "the mechanism is unknown"
Avoid: "nothing is known" (too strong - some things are known)

---

### 5. Self-Check Questions for Each Claim

Before making any causal claim in the manuscript, ask:

1. **Is there direct experimental evidence for causation?**
   - If yes: Can use stronger language
   - If no: Must use correlational language

2. **Are there alternative explanations?**
   - If yes: Must acknowledge them
   - If no: Can present as established

3. **Does the field consensus support this claim?**
   - If yes: Can present as established
   - If no: Must frame as hypothesis or debate

4. **Could a reader misinterpret this as more established than it is?**
   - If yes: Add explicit caveats
   - If no: Language is appropriate

---

### 6. Special Considerations for This Manuscript

#### Physical vs Molecular Claims

This manuscript makes a specific integrative claim: physical constraints and molecular regulation are bidirectionally coupled. This requires special care:

**Good pattern:**
"Physical constraint X creates a tendency. Molecular system Y detects and responds to this tendency, achieving outcome Z."

**Problematic pattern:**
"Physical constraint X causes outcome Z through molecular system Y."
(This implies unidirectional causality and oversimplifies)

#### Evolutionary Claims

**Good pattern:**
"Physical constraints likely existed in early cells. Molecular mechanisms for managing these constraints evolved progressively. The specific evolutionary sequence remains speculative."

**Problematic pattern:**
"Molecular regulation evolved sequentially to handle physical constraints."
(Presents as established when speculative)

---

### 7. Templates for Common Situations

#### Template 1: Correlation with Speculative Mechanism

"Observation X correlates with outcome Y (Citation). One hypothesis is that mechanism Z links X to Y, but this remains to be established. Alternative explanations include A and B."

#### Template 2: Physical-Molecular Integration

"Physical parameter P affects process Q (Citation). Molecular system M responds to P, achieving outcome R (Citation). This creates a bidirectional coupling where P influences M and M actively manages P."

#### Template 3: Ongoing Debate

"Question X remains actively debated in the field. Some groups argue Y (Citation), while others propose Z (Citation). The current consensus is that [balanced statement]."

#### Template 4: Established Mechanism

"Molecular mechanism M is well-established as necessary for process P. Mutations in M abolish P (Citation), and purified M can reconstitute P in vitro (Citation)."

---

### 8. Revision Checklist

For each section in the manuscript:

- [ ] Distinguish established mechanisms from correlations
- [ ] Add caveats for speculative claims
- [ ] Check "sensing" language for physical parameters
- [ ] Verify bidirectional coupling is emphasized, not unidirectional causality
- [ ] Ensure evolutionary claims are framed as speculative
- [ ] Check that examples (Caulobacter, SOS, etc.) are epistemically careful
- [ ] Verify language matches evidential strength
- [ ] Add explicit uncertainty statements where appropriate

---

## Conclusion

Applying epistemic care throughout the manuscript will:

1. **Strengthen rather than weaken** the core arguments by showing scientific rigor
2. **Model careful reasoning** for readers, especially students and early-career researchers
3. **Prevent future peer review concerns** by being upfront about uncertainty
4. **Enhance credibility** by acknowledging what is and isn't known
5. **Support the hierarchical framework** by showing it applies even when evidence is incomplete

The Caulobacter revision demonstrates that acknowledging uncertainty can STRENGTHEN an example rather than weakening it. Apply this principle throughout the manuscript.

---

**Next Steps:**
1. Apply these guidelines to Section 4.1 (Caulobacter) - use provided revised text
2. Review Section 2.1 (turgor pressure) for similar issues
3. Review Section 2.4 (crowding/phase separation) for controversial claims
4. Add epistemic caveats throughout as needed
5. Consider adding an "Epistemological Note" box to highlight this approach
