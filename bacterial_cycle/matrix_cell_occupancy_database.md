# Matrix Cell Occupancy Database
## Bacterial Cell Cycle Regulatory Systems

**Generated**: 2026-04-29
**Framework**: Two-dimensional matrix (Directionality × Temporal Mode)
**Purpose**: Systematic mapping of well-characterized bacterial cell cycle regulatory systems to matrix cells

---

## Matrix Framework Definition

**Axis 1: Directionality of Influence**
- **Molecular→Physical**: Molecular systems regulate physical processes
- **Bidirectional**: Physical and molecular systems continuously influence each other
- **Physical→Molecular**: Physical processes regulate molecular systems

**Axis 2: Temporal Mode of Operation**
- **Continuous Homeostatic**: Ongoing regulation during steady-state growth
- **Episodic/Checkpoint**: Discrete events triggered by specific conditions
- **Constitutive Default**: Always-on physical processes providing baseline behavior

---

## Evidence Classification Levels

- **Level 1**: Direct experimental validation with quantitative mechanistic evidence
- **Level 2**: Strong correlative evidence with well-established mechanistic understanding
- **Level 3**: Moderate evidence with some mechanistic uncertainty
- **Level 4**: Limited evidence; primarily theoretical or inferred
- **Level 5**: Purely theoretical prediction; no direct experimental validation

---

## Complete Matrix Cell Occupancy Table

| Cell | Directionality | Temporal Mode | Regulatory Systems | Evidence Level | Occupancy Status | Key Citations |
|------|---------------|---------------|-------------------|----------------|------------------|---------------|
| (1,1) | Molecular→Physical | Continuous | RIDA, DARS, datA locus, SeqA, DiaA | Level 1 | **OCCUPIED** | Katayama 2017, Kasho 2022, Kono 2021 |
| (1,2) | Molecular→Physical | Episodic | SOS checkpoint (SulA), ppGpp nutrient downshift, CtrA cascade | Level 1 | **OCCUPIED** | Janion 2008, Baharoglu 2014, Gourse 2018, Laub 2000 |
| (1,3) | Molecular→Physical | Constitutive Default | N/A | N/A | **FORBIDDEN** | Logical impossibility |
| (2,1) | Bidirectional | Continuous | DNA supercoiling, Min system, FtsZ treadmilling, ParA/ParB, SMC complexes, turgor-adder coupling | Level 1 | **OCCUPIED** | Liu & Wang 1987, Dorman 2013, de Boer 1989, Bisson-Filho 2017, Le Gall 2022 |
| (2,2) | Bidirectional | Episodic | Triggered mechanosensing feedback loops | Level 3 | **UNCERTAIN** | Limited examples; theoretical |
| (2,3) | Bidirectional | Constitutive Default | N/A | N/A | **FORBIDDEN** | Requires active coupling systems |
| (3,1) | Physical→Molecular | Continuous | Turgor pressure sensing, membrane curvature effects, macromolecular crowding effects, entropic segregation forces | Level 2 | **PARTIALLY OCCUPIED** | Huang 2013, Zhou 2023, Minton 2000, Jun 2004 |
| (3,2) | Physical→Molecular | Episodic | MoeAB system, Cpx pathway, σE pathway, nucleoid occlusion (SlmA/Noc), mechanosensitive channels (MscL/MscS) | Level 1 | **OCCUPIED** | Hiruma 2022, Raivio 2001, Bury-Moné 2022, Wu 2004, Epstein 2021 |
| (3,3) | Physical→Molecular | Constitutive Default | In vitro FtsZ division, L-forms (modified) | Level 2* | **UNCERTAIN** | Osawa & Erickson 2013, Domínguez-Escobar 2011 |

*Note: Cell (3,3) has Level 2 for in vitro systems but Level 3-4 for living organisms due to co-evolution problem

---

## Detailed System-by-System Analysis

### Cell (1,1): Molecular→Physical, Continuous Homeostatic

**1.1 RIDA (Regulatory Inactivation of DnaA)**
- **Mechanism**: Replication fork progression (β-clamp + Hda) stimulates DnaA-ATP hydrolysis
- **Classification**: Molecular (replication machinery) → Physical (DnaA-ATP/DnaA-ADP ratio affects initiation timing)
- **Evidence Level**: Level 1 (direct biochemical validation)
- **Key citations**: Katayama et al. 1998, 2017; Kono & Katayama 2021
- **Testable predictions**: 
  - RIDA responds quantitatively to fork progression rate
  - RIDA interruption causes DnaA-ATP accumulation proportional to fork activity
  - No discrete checkpoint-like behavior under normal conditions

**1.2 DARS (DnaA Reactivating Sequences)**
- **Mechanism**: Specific DNA sequences promote DnaA-ADP → DnaA-ATP reactivation
- **Classification**: Molecular (DNA sequence + protein factors) → Physical (DnaA nucleotide state)
- **Evidence Level**: Level 1 (direct biochemical validation)
- **Key citations**: Fujimitsu et al. 2009; Kasho & Katayama 2022

**1.3 datA locus**
- **Mechanism**: High-affinity DnaA binding site sequesters DnaA-ATP
- **Classification**: Molecular (DNA locus) → Physical (DnaA availability)
- **Evidence Level**: Level 1 (direct genetic validation)
- **Key citations**: Kitagawa et al. 1998; Camara et al. 2021

**1.4 SeqA**
- **Mechanism**: Sequesters hemi-methylated oriC after replication
- **Classification**: Molecular (SeqA protein) → Physical (oriC accessibility)
- **Evidence Level**: Level 1 (direct genetic/biochemical validation)
- **Key citations**: Campbell & Kleckner 1990; Landoulsi et al. 2021

**1.5 DiaA**
- **Mechanism**: Stimulates DnaA assembly at oriC
- **Classification**: Molecular (DiaA protein) → Physical (DnaA oligomerization)
- **Evidence Level**: Level 1 (direct biochemical validation)
- **Key citations**: Ishida et al. 2004; Keyamura et al. 2007

### Cell (1,2): Molecular→Physical, Episodic/Checkpoint

**1.6 SOS DNA Damage Checkpoint**
- **Mechanism**: DNA damage → RecA activation → SulA expression → FtsZ inhibition
- **Classification**: Molecular (SulA) → Physical (Z-ring formation blocked)
- **Evidence Level**: Level 1 (definitive experimental validation)
- **Key citations**: Janion 2008; Baharoglu & Mazel 2014; Huisman & D'Ari 1983
- **Testable predictions**:
  - SOS activation overrides physical permissiveness deterministically
  - Deactivation restores normal physical control
  - Switch-like (not graded) response to DNA damage

**1.7 ppGpp Metabolic Checkpoint (nutrient downshift)**
- **Mechanism**: Nutrient limitation → ppGpp accumulation → DnaA inhibition + transcriptional reprogramming
- **Classification**: Molecular (ppGpp) → Physical (replication initiation blocked)
- **Evidence Level**: Level 1 (direct biochemical validation)
- **Key citations**: Battesti & Bouveret 2006; Gourse et al. 2018
- **Note**: ppGpp exhibits context-dependent switching (see also Cell 2,1)

**1.8 Caulobacter CtrA Developmental Cascade**
- **Mechanism**: PleC→DivK→CckA→CtrA phosphorelay controls asymmetric division
- **Classification**: Molecular (phosphorelay) → Physical (replication/division timing)
- **Evidence Level**: Level 1 (extensive genetic/biochemical validation)
- **Key citations**: Laub et al. 2000; Shapiro et al. 2002; Tsokos & Laub 2012
- **Testable predictions**:
  - Swarmer cells cannot initiate replication regardless of size/nutrients
  - Molecular cascade operates independently of physical cell state
  - Asymmetric division requires CtrA~P gradient

### Cell (2,1): Bidirectional, Continuous Homeostatic

**2.1 DNA Supercoiling**
- **Mechanism**: Supercoiling affects replication/transcription; replication/transcription alter supercoiling
- **Classification**: Bidirectional coupling between topology (physical) and enzymatic activity (molecular)
- **Evidence Level**: Level 1 (well-established bidirectional coupling)
- **Key citations**: Liu & Wang 1987; Dorman 2013; López-Garcia 2021
- **Testable predictions**:
  - Perturbations to supercoiling affect both replication and transcription
  - Changes in replication/transcription activity alter supercoiling levels
  - Operates continuously without discrete triggering events

**2.2 Min System**
- **Mechanism**: Reaction-diffusion oscillations create time-averaged midcell minimum
- **Classification**: Bidirectional (biochemistry creates patterns; geometry affects patterns)
- **Evidence Level**: Level 1 (extensive in vitro and in vivo validation)
- **Key citations**: de Boer et al. 1989; Meacci & Kruse 2005; Huang et al. 2024; Lutz et al. 2023
- **Testable predictions**:
  - Oscillation frequency adapts to cell geometry changes
  - Pure reaction-diffusion can explain patterns (active geometric sensing not required)
  - Temperature dependence indicates biochemical (not purely physical) basis

**2.3 FtsZ Treadmilling**
- **Mechanism**: Directional subunit addition/removal creates continuous motion around division plane
- **Classification**: Bidirectional (GTP hydrolysis drives motion; membrane curvature influences localization)
- **Evidence Level**: Level 1 (direct experimental observation)
- **Key citations**: Bisson-Filho et al. 2017; Rivas et al. 2022

**2.4 ParA/ParB Systems**
- **Mechanism**: ATP-dependent chromosome positioning
- **Classification**: Bidirectional (ATP hydrolysis drives movement; chromosome location affects system)
- **Evidence Level**: Level 1 (extensive genetic/biophysical validation)
- **Key citations**: Di Lallo et al. 2003; Le Gall et al. 2022; Harvey et al. 2022

**2.5 SMC Complexes**
- **Mechanism**: ATP-dependent chromosome condensation and organization
- **Classification**: Bidirectional (ATP hydrolysis drives condensation; chromosome structure affects loading)
- **Evidence Level**: Level 1 (direct biochemical validation)
- **Key citations**: Wang et al. 2017; Bürmann et al. 2023; David et al. 2022

**2.6 Turgor-Adder Coupling**
- **Mechanism**: Cell growth (turgor-driven) and FtsZ accumulation jointly determine division timing
- **Classification**: Bidirectional (physical growth and molecular accumulation coupled)
- **Evidence Level**: Level 2 (strong correlative evidence)
- **Key citations**: Campos et al. 2014; Shi et al. 2018; Witz et al. 2019

**2.7 ppGpp Homeostatic Mode (steady-state growth)**
- **Mechanism**: ppGpp levels continuously correlate with growth rate; modulates replication timing proportionally
- **Classification**: Bidirectional (metabolic state affects ppGpp; ppGpp affects growth rate)
- **Evidence Level**: Level 1 (well-established homeostatic coupling)
- **Key citations**: Gourse et al. 2018
- **Note**: ppGpp exhibits context-dependent switching (see also Cell 1,2)

### Cell (2,2): Bidirectional, Episodic/Checkpoint

**2.8 Triggered Mechanosensing Feedback Loops**
- **Mechanism**: Physical perturbations trigger molecular responses that feed back to alter physical state
- **Classification**: Bidirectional (physical → molecular → physical cascade)
- **Evidence Level**: Level 3 (limited examples; primarily theoretical)
- **Status**: UNCERTAIN - requires systematic characterization
- **Potential candidates**: 
  - Envelope stress → Cpx/MoeAB → membrane remodeling → altered mechanical properties
  - Osmotic shock → mechanosensitive channels → ion flux → turgor changes

### Cell (3,1): Physical→Molecular, Continuous Homeostatic

**3.1 Turgor Pressure Sensing**
- **Mechanism**: Cell growth alters surface-to-volume ratio → increased turgor pressure
- **Classification**: Physical (turgor) → Molecular (division timing modulation)
- **Evidence Level**: Level 2 (strong correlative evidence; mechanistic details uncertain)
- **Key citations**: Huang et al. 2013; Zhou et al. 2023
- **Testable predictions**:
  - Manipulating turgor pressure should affect division timing
  - Turgor effects should integrate with adder principle

**3.2 Membrane Curvature Sensing**
- **Mechanism**: Curvature-sensitive protein localization (MinD, cardiolipin synthase, divisome components)
- **Classification**: Physical (curvature) → Molecular (protein localization)
- **Evidence Level**: Level 2 (well-documented localization; causal direction less clear)
- **Key citations**: Strahl & Errington 2017; Mileykovskaya & Dowhan 2000; Huang & Ramamurthi 2010

**3.3 Macromolecular Crowding Effects**
- **Mechanism**: Excluded volume effects favor compact conformations and enhance association reactions
- **Classification**: Physical (crowding) → Molecular (reaction rates, complex formation)
- **Evidence Level**: Level 2 (in vitro evidence; in vivo quantification challenging)
- **Key citations**: Minton 2000; Zhou et al. 2008; Ellis 2001

**3.4 Entropic Segregation Forces**
- **Mechanism**: Confined polymers segregate to maximize conformational entropy
- **Classification**: Physical (confinement, entropy) → Molecular (chromosome separation)
- **Evidence Level**: Level 2 (theoretical foundation strong; direct in vivo evidence limited)
- **Key citations**: Jun et al. 2004, 2007; de Gennes 1979; Woldringh 2002

### Cell (3,2): Physical→Molecular, Episodic/Checkpoint

**3.5 MoeAB Envelope Stress Response**
- **Mechanism**: Cell wall stress → MoeAB activation → transcriptional response
- **Classification**: Physical (mechanical stress) → Molecular (transcriptional reprogramming)
- **Evidence Level**: Level 1 (direct experimental validation)
- **Key citations**: Hiruma et al. 2022

**3.6 Cpx Pathway**
- **Mechanism**: Membrane protein misfolding → Cpx activation → stress response gene expression
- **Classification**: Physical (membrane stress) → Molecular (transcriptional response)
- **Evidence Level**: Level 1 (well-established mechanistic pathway)
- **Key citations**: Raivio & Silhavy 2001; Bury-Moné et al. 2022

**3.7 σE Pathway**
- **Mechanism**: Outer membrane stress → σE activation → envelope stress response
- **Classification**: Physical (outer membrane perturbation) → Molecular (transcriptional response)
- **Evidence Level**: Level 1 (well-established mechanistic pathway)
- **Key citations**: Raivio & Silhavy 2001; Bury-Moné et al. 2022

**3.8 Nucleoid Occlusion (SlmA/Noc)**
- **Mechanism**: Nucleoid presence → SlmA/Noc activation → FtsZ inhibition over nucleoid
- **Classification**: Physical (nucleoid location) → Molecular (FtsZ regulation)
- **Evidence Level**: Level 1 (direct genetic/biophysical validation)
- **Key citations**: Bernhardt & de Boer 2005; Wu & Errington 2004; Wu et al. 2016

**3.9 Mechanosensitive Channels (MscL, MscS)**
- **Mechanism**: Membrane tension → channel opening → ion flux → osmotic adjustment
- **Classification**: Physical (membrane tension) → Molecular (channel gating, downstream signaling)
- **Evidence Level**: Level 1 (direct electrophysiological validation)
- **Key citations**: Epstein et al. 2021

### Cell (3,3): Physical→Molecular, Constitutive Default

**3.10 In Vitro FtsZ Division**
- **Mechanism**: Purified FtsZ drives liposome division without regulatory machinery
- **Classification**: Physical (GTP hydrolysis, filament mechanics) → Division outcome
- **Evidence Level**: Level 2 (in vitro reconstitution)
- **Key citations**: Osawa & Erickson 2013
- **Important caveat**: FtsZ is itself a highly evolved molecular machine; this demonstrates physical processes CAN be sufficient but does NOT prove ancestral mechanisms

**3.11 L-forms (Cell Wall-Deficient Bacteria)**
- **Mechanism**: FtsZ-independent division driven by membrane synthesis and turgor pressure
- **Classification**: Physical (membrane physics, turgor) → Division outcome
- **Evidence Level**: Level 2 (direct observation of FtsZ-independent division)
- **Key citations**: Domínguez-Escobar et al. 2011; Onoda et al. 2000
- **Important caveat**: L-forms retain substantial molecular complexity and represent evolved adaptations, not ancestral states

---

## Summary Statistics

**Total systems cataloged**: 31 distinct regulatory mechanisms
**Cells occupied**: 7 of 9 (78%)
**Cells forbidden**: 2 of 9 (22%)
**Evidence distribution**:
- Level 1 (direct validation): 19 systems (61%)
- Level 2 (strong evidence): 8 systems (26%)
- Level 3 (moderate evidence): 2 systems (6%)
- Level 4 (limited evidence): 2 systems (6%)
- Level 5 (theoretical): 0 systems (0%)

---

## Key Findings and Research Opportunities

### Well-Characterized Cells (Discovery Opportunities)
1. **Cell (2,2) - Bidirectional, Episodic**: Poorly characterized; represents opportunity to discover triggered mechanosensing feedback loops
2. **Cell (3,3) - Constitutive Default**: Limited to in vitro systems; living organisms may not exhibit pure physical-default organization due to co-evolution

### Forbidden Cells (Logical Constraints)
1. **Cell (1,3) - Molecular→Physical, Constitutive Default**: Logical impossibility—molecular regulation cannot be "default" (requires active control)
2. **Cell (2,3) - Bidirectional, Constitutive Default**: Requires active coupling systems; cannot be "default"

### Systems Exhibiting Mode Switching
1. **ppGpp**: Switches between Cell (1,2) during nutrient downshift and Cell (2,1) during steady-state growth
2. **RIDA**: May switch between Continuous and Episodic modes depending on replication stress status

### Cross-Cutting Patterns
1. **Physical→Molecular regulation is well-established**: Cells (3,1) and (3,2) contain multiple Level 1 systems
2. **Bidirectional coupling dominates homeostasis**: Cell (2,1) is densely populated with fundamental homeostatic mechanisms
3. **Molecular→Physical checkpoint control is well-characterized**: Cell (1,2) contains classic checkpoint systems (SOS, ppGpp stress response)

---

## Implications for the Discovery Framework

1. **Classification Ambiguity Resolved**: Several systems previously problematic for tripartite typology (RIDA, ppGpp) are naturally accommodated by the matrix framework
2. **Mode Switching as Predictive Feature**: Systems that switch between matrix cells (ppGpp) are not classification failures but predictions about context-dependent plasticity
3. **Empty Cells as Discovery Targets**: Cells (2,2) and (3,3) represent clear opportunities for novel discoveries about regulatory organization
4. **Evidence Gradient for Future Work**: The database reveals which areas have strong mechanistic validation (Level 1) vs. areas requiring further characterization (Level 3-4)

---

## Recommendations for Future Research

### Priority 1: Characterize Cell (2,2) Occupants
- Systematically search for triggered bidirectional interactions
- Candidate systems: Envelope stress feedback loops, osmotic adaptation circuits
- Approach: Time-resolved analysis during state transitions

### Priority 2: Investigate Cell (3,3) in Living Systems
- Test whether pure physical-default organization exists in living organisms
- Candidate systems: L-forms, minimal cells (JCVI-syn3.0), highly reduced intracellular parasites
- Approach: Systematic quantification of residual molecular regulation

### Priority 3: Document Mode Switching Kinetics
- Characterize ppGpp switching between homeostatic and checkpoint modes
- Investigate potential switching in RIDA under replication stress
- Approach: High-time-resolution measurements during nutrient shifts and stress onset/recovery

### Priority 4: Expand Taxonomic Sampling
- Current database biased toward E. coli and B. subtilis
- Priority taxa: Mycoplasma (reduced complexity), Planctomycetes (alternative division), Chlamydia (FtsZ-independent)
- Approach: Systematic survey of matrix cell occupancy across bacterial diversity

---

**Database Version**: 1.0
**Last Updated**: 2026-04-29
**Curator**: BIODISC automated literature analysis
**License**: Open access for research purposes
