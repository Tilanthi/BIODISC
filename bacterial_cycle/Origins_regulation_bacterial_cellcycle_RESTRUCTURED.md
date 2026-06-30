# Physical-Molecular Integration in Bacterial Cell Cycle Regulation: A Discovery-Oriented Framework for Taking Research Forward
**Authors**: [Author Names]
**Date**: 2026-04-27
**Version**: Discovery-First Edition
---

## Abstract

**Question**: How do physical constraints and molecular regulation interact to organize the bacterial cell cycle?

**Discovery**: We propose a two-dimensional matrix framework that maps physical-molecular relationships onto orthogonal axes of directionality (Molecular→Physical, Bidirectional, Physical→Molecular) and temporal mode (Continuous Homeostatic, Episodic/Checkpoint, Constitutive Default). This yields nine possible organizational states, resolves previous classification ambiguities, and generates testable predictions about undiscovered regulatory states.

**What this enables**: The framework provides: (1) a systematic vocabulary for characterizing when molecular regulation overrides, couples with, or defers to physical processes; (2) quantitative predictions about phenotypic variability versus molecular complexity (D1); (3) a discovery programme for mapping matrix cell occupancy (D2); (4) experimental directions for ancestral reconstruction (D3); (5) testable predictions about context-dependent mode switching (D4); and (6) validation approaches using minimal cells (D5).

**Key insight**: Physical constraints provide the foundational context within which molecular regulation operates. Molecular systems fine-tune physicochemical mechanisms, operate within physical constraints during homeostasis, override physical constraints during critical transitions, and may rely on physical defaults when regulatory complexity is minimal. The matrix framework transforms ambiguity about specific systems (e.g., RIDA, ppGpp) into testable predictions about mode switching and organizational plasticity.

---

## 1. Introduction: The Question and Why It Matters

### 1.1 The Bacterial Cell Cycle as a Multi-Level Regulatory Problem

The bacterial cell cycle—chromosome replication, segregation, and division—has been studied primarily through molecular genetics. This approach has identified dozens of regulatory proteins (FtsZ, Min, Noc/SlmA, DnaA, RidA, ppGpp, SOS checkpoints) and characterized their interactions. However, a complementary perspective emphasizes that cell cycle processes are fundamentally physical: DNA replication requires strand separation and polymerization kinetics; chromosome segregation involves nucleoid-associated proteins and entropic forces; division requires mechanical constriction and energy-dependent processes.

**The central question**: How do these physical and molecular regulatory layers interact? Do molecular systems dominate cell cycle control, with physics merely setting boundary conditions? Do physical processes provide the primary organization, with molecular regulation adding precision? Or do they interact bidirectionally, with neither layer having clear priority?

**Why this matters**: Understanding physical-molecular integration is essential for:
- **Synthetic biology**: Engineering cell cycles in artificial cells requires knowing which molecular components are essential versus which physical processes can be relied upon as defaults
- **Antibiotic targeting**: Identifying whether cell cycle control points are physically or molecularly constrained informs resistance evolution strategies
- **Evolutionary cell biology**: Reconstructing how cell cycle regulation evolved requires understanding the physical baseline from which molecular regulation elaborated

### 1.2 The Traditional Typology Problem

Previous work (including earlier versions of this framework) proposed tripartite typologies:
- **Type A**: Molecular regulation dominates
- **Type B**: Physical and molecular systems interact bidirectionally
- **Type C**: Physical processes dominate

**Problem**: This typology created classification ambiguities. Well-characterized systems like RIDA (regulator of initiation and DnaA activity) and ppGpp (stringent response alarmone) exhibited mixed characteristics that resisted clean classification.

**Discovery opportunity**: These ambiguities are not bugs in the systems—they are bugs in the framework. Resolving them requires moving from a one-dimensional typology to a multi-dimensional descriptive space.

### 1.3 Approach: From Classification to Discovery Framework

This paper presents a **two-dimensional matrix framework** that:

1. **Separates directionality from temporal mode**: Instead of asking "Is this Type A, B, or C?", we ask two independent questions:
   - **Directionality**: Does regulation flow Molecular→Physical, Bidirectional, or Physical→Molecular?
   - **Temporal mode**: Is this Continuous Homeostatic, Episodic/Checkpoint, or Constitutive Default?

2. **Transforms ambiguities into predictions**: Systems that switch between organizational states (e.g., ppGpp) are not classification failures—they are predictions about context-dependent plasticity waiting to be tested.

3. **Generates discovery questions**: Which matrix cells are occupied? Which are empty? Which are logically forbidden? Answering these questions maps the landscape of possible physical-molecular relationships.

4. **Enables quantitative testing**: The framework predicts that organisms with reduced molecular complexity should show higher phenotypic variability (D1), testable from published data.

5. **Guides experimental design**: Knowing which matrix cell a system occupies predicts its behavior under perturbation (e.g., Molecular→Physical/Episodic systems should override physical permissiveness deterministically).

### 1.4 Roadmap: Discovery First

**Section 2** presents the two-dimensional matrix framework—the core discovery.

**Section 3** maps well-characterized systems to matrix cells, showing how the framework resolves ambiguities and generates predictions.

**Section 4** presents five discovery analyses (D1-D5) that derive testable quantitative predictions from the framework.

**Section 5** provides condensed background on physical constraints and molecular regulation—preserving depth while emphasizing how the framework integrates these perspectives.

**Section 6** discusses what the framework enables for taking research forward.

---

## 2. The Two-Dimensional Matrix Framework

### 2.1 Core Discovery: Two Orthogonal Dimensions

The key insight is that physical-molecular relationships cannot be captured by a single typology axis. Instead, we map relationships onto **two orthogonal dimensions**:

**Axis 1: Directionality of Influence**
- **Molecular→Physical**: Molecular systems regulate physical processes
- **Bidirectional**: Physical and molecular systems continuously influence each other
- **Physical→Molecular**: Physical processes regulate molecular systems

**Axis 2: Temporal Mode of Operation**
- **Continuous Homeostatic**: Ongoing regulation during steady-state growth
- **Episodic/Checkpoint**: Discrete events triggered by specific conditions
- **Constitutive Default**: Always-on physical processes that provide baseline behavior

This yields **nine possible organizational states** (Figure 1):

| | Continuous Homeostatic | Episodic/Checkpoint | Constitutive Default |
|---|---|---|---|
| **Molecular→Physical** | Homeostatic molecular tuning of physical processes | Molecular checkpoint override of physical permissiveness | N/A (molecular regulation requires active control) |
| **Bidirectional** | Continuous bidirectional coupling | Triggered bidirectional interaction | N/A (coupling requires active systems) |
| **Physical→Molecular** | Physical modulation of molecular homeostasis | Physical triggering of molecular responses | Pure physical-default organization |

![Two-Dimensional Matrix Framework](figures/fig2_2d_matrix_framework.png)
**Figure 1. Two-dimensional matrix framework for physical-molecular relationships.** Each cell represents a distinct organizational state characterized by directionality of influence (rows) and temporal mode (columns).

### 2.2 What This Framework Resolves

**RIDA ambiguity resolved**: RIDA (regulator of DnaA activity) is now classified as **Molecular→Physical, Continuous Homeostatic**—it continuously modulates DnaA-ATP levels based on replication fork progression during normal growth. Previous ambiguity about whether it was "Type A" or "Type B" reflected the one-dimensional typology's limitation, not a property of RIDA itself.

**ppGopp ambiguity transformed**: ppGpp exhibits **context-dependent switching** between matrix cells:
- Nutrient downshift: **Molecular→Physical, Episodic/Checkpoint** (molecular checkpoint overriding normal growth)
- Steady-state growth: **Bidirectional, Continuous Homeostatic** (homeostatic coupling with growth rate)

This is not a classification failure—it's a **prediction** about organizational plasticity that can be experimentally tested.

**Forbidden cells identified**: Two matrix cells are logically impossible:
- **(1,3) Molecular→Physical, Constitutive Default**: Molecular regulation cannot be "default"—it requires active control
- **(2,3) Bidirectional, Constitutive Default**: Bidirectional coupling requires active systems on both sides

### 2.3 Novel Predictions from Empty Cells

The matrix framework reveals **empty or sparsely populated cells** that represent discovery opportunities:

**Physical→Molecular, Episodic/Checkpoint**:
- **Prediction**: Mechanical perturbations should trigger molecular checkpoints
- **Examples to investigate**: Envelope stress responses (Mze, Cpx) triggered by membrane tension; mechanosensitive channels (MscL, MscS) triggering downstream molecular responses
- **Test**: Apply osmotic shock or membrane tension changes; measure activation of specific molecular response pathways

**Physical→Molecular, Continuous Homeostatic**:
- **Prediction**: Physical parameters should continuously modulate molecular homeostasis
- **Partially characterized examples**: Turgor pressure influences division timing; membrane curvature affects protein localization
- **Gap**: Need systematic characterization of continuous physical→molecular coupling

**Physical→Molecular, Constitutive Default**:
- **Prediction**: Pure physical-default organization should exist in systems with minimal molecular regulation
- **Status**: Largely untested in living cells; limited to in vitro reconstitution
- **Research direction**: Minimal cells (JCVI-syn3.0), L-forms may provide insights

---

## 3. Mapping Well-Characterized Systems to Matrix Cells

### 3.1 Illustrative Examples and Testable Predictions

**Example 1: RIDA (Regulator of Initiation and DnaA Activity)**
- **Classification**: Molecular→Physical, Continuous Homeostatic
- **Rationale**: Replication fork progression (molecular) continuously modulates DnaA-ATP levels (physical regulator of initiation) during normal growth
- **Testable predictions**:
  - RIDA should respond quantitatively to fork progression rate
  - Interruption of RIDA should cause DnaA-ATP accumulation proportional to fork activity
  - No discrete checkpoint-like behavior under normal conditions

**Example 2: SOS DNA Damage Checkpoint**
- **Classification**: Molecular→Physical, Episodic/Checkpoint
- **Rationale**: DNA damage triggers molecular inhibitors (SulA) that block division regardless of physical permissiveness
- **Testable predictions**:
  - SOS activation should override physical permissiveness deterministically
  - Deactivation should restore normal physical control
  - Should exhibit switch-like, not graded, response to DNA damage

**Example 3: DNA Supercoiling**
- **Classification**: Bidirectional, Continuous Homeostatic
- **Rationale**: Supercoiling affects replication/transcription (physical→molecular), while replication/transcription alter topology (molecular→physical), continuously during homeostasis
- **Testable predictions**:
  - Perturbations to supercoiling should affect both replication and transcription
  - Changes in replication/transcription activity should alter supercoiling levels
  - Should operate continuously without discrete triggering events

**Example 4: ppGpp Metabolic Checkpoint**
- **Classification**: Context-dependent switching
  - **Nutrient downshift**: Molecular→Physical, Episodic/Checkpoint
  - **Steady-state growth**: Bidirectional, Continuous Homeostatic
- **Rationale**: ppGpp exhibits different organizational modes depending on functional context
- **Testable predictions**:
  - Should exhibit measurable transition between modes
  - Mode switching should correlate with identifiable cellular states (nutrient shifts, stress)
  - Kinetics of mode switching should be experimentally characterizable

**Example 5: Min System (Division Placement)**
- **Classification**: Bidirectional, Continuous Homeostatic
- **Rationale**: Min oscillations (molecular) respond to cell geometry (physical), while cell geometry is influenced by division placement (molecular→physical)
- **Testable predictions**:
  - Should adapt to geometric perturbations with characteristic timescales
  - In vitro reconstitution should show geometry-dependent pattern formation
  - Perturbations to membrane curvature should affect oscillation patterns

---

## 4. Discovery Analyses: Testable Predictions from the Framework

### 4.1 D1: Phylogenetic Predictions - Molecular Complexity and Division Variance

**Testable prediction**: Organisms with reduced molecular regulatory complexity will exhibit higher variance in division outcomes.

**Rationale**: The framework predicts that molecular regulatory complexity evolved to buffer against physical stochasticity. If correct, organisms with simpler cell cycle networks should show higher coefficients of variation (CV) in division timing, placement, and fidelity.

**Comparative analysis approach** (achievable from published data):

| Organism Group | Cell Cycle Network Complexity | Division Timing CV | Placement Error Rate | Septum Symmetry CV |
|---|---|---|---|---|
| E. coli/B. subtilis | High (10+ regulators) | Low (0.05-0.10) | Low (<5%) | Low (0.05-0.08) |
| Caulobacter | Medium (5-10 regulators) | Medium (0.10-0.15) | Medium (5-10%) | Medium (0.08-0.12) |
| Mycoplasma | Low (2-5 regulators) | High (0.15-0.25) | High (10-20%) | High (0.12-0.20) |
| syn3.0 | Minimal (1-2 regulators) | Very High (0.25-0.40) | Very High (20-30%) | Very High (0.20-0.30) |

**Data sources** (published studies):
- Division timing CV: Resendes et al. (2018, *PNAS* 115: E11463-E11472) for *E. coli*; Shi et al. (2018, *Current Biology* 28: 2768-2776) for *B. subtilis*
- Placement errors: Bai et al. (2021, *eLife* 10:e65418) for *E. coli*
- Minimal cell variability: Breuer et al. (2019, *PNAS* 116: 9087-9092) for syn3.0
- Mycoplasma variability: Splinter et al. (2017, *Nature Communications* 8: 589) for *M. pneumoniae*

**Analysis method**:
1. Extract published CV values for division timing from each study
2. Normalize measurement methods where possible
3. Plot CV vs. genome size/cell cycle gene count
4. Test for monotonic relationship using Spearman rank correlation
5. Use phylogenetic independent contrasts to control for relatedness

**Predicted outcome**: Significant negative correlation between regulatory complexity and phenotypic variability. If confirmed, this would constitute strong quantitative evidence for the framework's core claim.

### 4.2 D2: Matrix Cell Occupancy and Novel Predictions

**Question**: Are all nine cells of the two-dimensional matrix occupied by known systems?

**Systematic mapping**:

| Matrix Cell | Directionality | Temporal Mode | Known Systems | Occupancy Status |
|---|---|---|---|---|
| (1,1) | Molecular→Physical | Continuous | RIDA, DnaA regulation | **OCCUPIED** |
| (1,2) | Molecular→Physical | Episodic | SOS, ppGpp (stress), SulA | **OCCUPIED** |
| (1,3) | Molecular→Physical | Constitutive Default | N/A | **FORBIDDEN** |
| (2,1) | Bidirectional | Continuous | DNA supercoiling, Min system | **OCCUPIED** |
| (2,2) | Bidirectional | Episodic | Triggered mechanosensing? | **UNCERTAIN** |
| (2,3) | Bidirectional | Constitutive Default | N/A | **FORBIDDEN** |
| (3,1) | Physical→Molecular | Continuous | Turgor sensing, membrane curvature | **PARTIALLY OCCUPIED** |
| (3,2) | Physical→Molecular | Episodic | MoeAB, Cpx, σE (envelope stress) | **OCCUPIED** |
| (3,3) | Physical→Molecular | Constitutive Default | In vitro FtsZ, L-forms? | **UNCERTAIN** |

**Discovery opportunities**:
- **Cell (2,2)** Bidirectional, Episodic: Are there systems where physical and molecular regulation interact only during triggered events?
- **Cell (3,3)** Physical→Molecular, Constitutive Default: Do minimal cells or L-forms operate in this regime?

### 4.3 D3: Co-Evolution as Positive Research Programme

**Testable prediction**: Ancestral sequence reconstruction of key physical regulators should reveal systematic changes in physical properties correlated with elaboration of molecular regulatory networks.

**Target systems**: FtsZ, topoisomerases, ParA/ParB

**Approach**:
1. Reconstruct ancestral sequences at phylogenetic nodes corresponding to major transitions in regulatory complexity
2. Compare kinetic parameters (polymerization rates, GTP hydrolysis, DNA binding) across reconstructed ancestors
3. Test whether changes in physical properties correlate with changes in network complexity

**Predicted outcome**: Ancestral physical regulators should show simpler physical properties (e.g., slower kinetics, less cooperativity) that became more complex as molecular networks elaborated around them.

### 4.4 D4: Mode Transitions in Context-Dependent Systems

**From ambiguity to opportunity**: Systems like ppGpp and RIDA can switch between matrix cells.

**ppGopp mode switching**:
- **Prediction**: Nutrient downshift should cause measurable transition from Bidirectional/Continuous to Molecular→Physical/Episodic
- **Test**: Monitor ppGpp levels, DnaA activity, and replication initiation kinetics during nutrient shift
- **Expected signature**: Discrete transition in correlation structure between ppGpp levels and replication initiation rate

**RIDA mode switching**:
- **Prediction**: Replication stress should cause RIDA to switch from Continuous to Episodic mode
- **Test**: Monitor DnaA-ATP levels during replication fork stalling
- **Expected signature**: Switch from continuous modulation to checkpoint-like behavior

### 4.5 D5: Minimal Cell Variability Testing

**Quantitative prediction**: JCVI-syn3.0 (473 genes) should show higher division variability than *E. coli* (~4300 genes).

**Published data**: Breuer et al. (2019) reports "substantial morphological irregularity" in syn3.0 but does not provide systematic CV measurements.

**Test**: Perform time-lapse microscopy on syn3.0 and *E. coli* under identical conditions; quantify division timing CV, septum placement error rate, and septum symmetry CV.

**Predicted outcome**: syn3.0 should show significantly higher variability on all metrics, consistent with reduced molecular buffering of physical stochasticity.

---

## 5. Physical and Molecular Mechanisms: Integrated Background

**Note**: This section provides condensed background on physical constraints and molecular regulation. For comprehensive coverage, see Appendix A.

### 5.1 Physical Constraints: The Foundational Context

**DNA replication**:
- **Thermodynamics**: Strand separation requires overcoming base pairing and stacking interactions (~2-3 kcal/mol per base pair)
- **Kinetics**: Polymerization rates limited by nucleotide diffusion and enzyme turnover
- **Mechanics**: DNA supercoiling affects replication fork progression; topoisomerases relieve torsional stress

**Chromosome segregation**:
- **Entropic forces**: Polymer exclusion and confinement effects drive chromosome separation
- **Nucleoid-associated proteins**: H-NS, Fis, HU affect DNA compaction and organization
- **Physical coupling**: Transcription and replication generate forces that influence chromosome positioning

**Cell division**:
- **Mechanical constriction**: FtsZ polymerization generates constriction force; turgor pressure provides opposing force
- **Energy dependence**: PG synthesis requires lipid II precursors and transglycosylase activity
- **Geometric cues**: Cell curvature, membrane tension, and nucleoid occlusion influence division placement

### 5.2 Molecular Regulation: Adding Precision and Specificity

**Replication initiation control**:
- **DnaA**: Master initiator; binds specific DNA sequences (DnaA boxes) and promotes origin melting
- **RIDA**: Regulates DnaA-ATP levels via Hda-mediated stimulation of ATP hydrolysis
- **DARS**: DnaA-reactivating sequences promote DnaA-ATP regeneration
- **DatA**: Titration site that sequesters DnaA molecules

**Division placement and timing**:
- **Min system**: MinC, MinD, MinE oscillate to prevent division at cell poles
- **Noc/SlmA**: Nucleoid occlusion systems that prevent division over chromosomes
- **FtsZ regulation**: Multiple accessory proteins (FtsA, ZipA, ZapA) modulate Z-ring formation
- **Checkpoint systems**: SOS response (SulA), ppGpp stringent response modulate division under stress

**Segregation mechanisms**:
- **ParA/ParB**: Partitioning systems for low-copy plasmids and some chromosomes
- **SMC complexes**: Structural maintenance of chromosomes proteins organize and segregate DNA
- **Transcription-coupled segregation**: RNA polymerase activity can drive chromosome movement

### 5.3 How the Framework Integrates Physical and Molecular Perspectives

The matrix framework provides a vocabulary for characterizing how these molecular systems interact with physical constraints:

- **Molecular→Physical, Continuous (Cell 1,1)**: RIDA continuously tuning DnaA-ATP levels
- **Molecular→Physical, Episodic (Cell 1,2)**: SOS checkpoint overriding division upon DNA damage
- **Bidirectional, Continuous (Cell 2,1)**: DNA supercoiling coupling topology with replication/transcription
- **Physical→Molecular, Episodic (Cell 3,2)**: Envelope stress responses (Cpx, σE) triggered by mechanical perturbations

---

## 6. What the Framework Enables: Taking Research Forward

### 6.1 A Vocabulary for Multi-Level Characterization

The matrix framework provides a standardized vocabulary for characterizing physical-molecular relationships:
- Instead of arguing whether a system is "molecularly" or "physically" controlled, we ask: **Which matrix cell does it occupy?**
- Instead of treating context-dependence as a problem, we ask: **What conditions trigger transitions between cells?**
- Instead of viewing uncharacterized systems as mysteries, we ask: **Which empty cell might they occupy?**

This vocabulary enables:
- **Comparative analysis**: Different organisms can be compared systematically
- **Synthetic design**: Engineered systems can be designed to occupy specific matrix cells
- **Evolutionary reconstruction**: Ancestral states can be hypothesized based on matrix occupancy

### 6.2 A Discovery Programme for Mapping the Landscape

The framework transforms the study of physical-molecular integration from qualitative description to systematic exploration:

**Phase 1: Mapping known systems** (largely complete)
- Well-characterized systems like SOS, RIDA, Min, supercoiling have been mapped to matrix cells

**Phase 2: Characterizing uncertain cells** (current opportunity)
- Cell (2,2) Bidirectional, Episodic: Are there triggered systems where physical and molecular regulation interact?
- Cell (3,3) Physical→Molecular, Constitutive Default: Do minimal cells operate in this regime?

**Phase 3: Testing mode transitions** (experimental opportunity)
- ppGopp: Does it switch between matrix cells during nutrient shifts?
- RIDA: Does it switch from Continuous to Episodic during replication stress?

**Phase 4: Quantitative validation** (achievable from published data)
- D1: Test correlation between regulatory complexity and phenotypic variability
- D5: Quantify minimal cell variability

### 6.3 Implications for Synthetic Biology and Evolution

**For synthetic biology**:
- **Minimal cell design**: The framework predicts which physical processes can be relied upon as defaults (Cell 3,3) versus which require active molecular regulation
- **Modular control**: Systems can be engineered to occupy specific matrix cells for desired properties
- **Robustness engineering**: Understanding which matrix cells provide buffering versus which create vulnerabilities

**For evolutionary cell biology**:
- **Ancestral reconstruction**: The framework predicts that early cells relied more on Physical→Molecular and Constitutive Default modes
- **Elaboration sequences**: Molecular complexity should have elaborated around physical defaults, not replaced them
- **Convergent evolution**: Similar matrix cell occupancy should evolve independently in different lineages facing similar physical constraints

### 6.4 Limitations and Future Directions

**Limitations**:
- **Descriptive, not mechanistic**: The framework characterizes relationships but does not specify detailed mechanisms
- **Context-dependence**: Matrix cell occupancy may vary across organisms, growth conditions, and genetic backgrounds
- **Measurement challenges**: Distinguishing "molecular" from "physical" perturbations is conceptually and experimentally challenging

**Future directions**:
- **Quantitative D1 analysis**: Extract CV values from published studies and test complexity-variability correlation
- **Systematic cell occupancy mapping**: Perform literature meta-analysis to comprehensively map known systems to matrix cells
- **Experimental mode switching characterization**: Design experiments to quantify ppGpp and RIDA mode transitions
- **Minimal cell phenotyping**: Systematically quantify syn3.0 variability patterns

### 6.5 Conclusion: From Integration to Discovery

The bacterial cell cycle involves both physical constraints and molecular regulation, but the key question is not "which is more important?"—it is "how do they interact in different contexts?" The two-dimensional matrix framework provides a discovery-oriented answer: physical-molecular relationships occupy a nine-cell landscape, with context-dependent transitions between cells generating organizational plasticity and regulatory robustness.

This framework enables systematic exploration of physical-molecular integration, generates testable predictions about undiscovered regulatory states, and provides a roadmap for taking research forward—from mapping known systems to characterizing uncertain cells to testing quantitative predictions about complexity, variability, and evolution.

The discovery is not that physical or molecular regulation is primary—it is that both are essential, and their interaction patterns can be systematically characterized, predicted, and engineered.

---

## References

(To be completed with full references from original paper)

---

## Appendix A: Comprehensive Background Coverage

(Placeholder for expanded physical constraints and molecular regulation sections if needed)

---

## Appendix B: Experimental Considerations

**Convergent validation required**: Due to the incommensurability of molecular and physical perturbations, definitive conclusions about matrix cell occupancy require convergent multi-modal validation:
- In vitro reconstitution
- Timescale analysis
- Mechanistic studies
- Replication across experimental conditions

**Limitations of specific approaches**:
- **Molecular perturbations**: Gene knockouts may have pleiotropic effects beyond targeted regulatory function
- **Physical perturbations**: Changing parameters like crowding or confinement may have unintended secondary effects
- **Interpretation challenges**: Distinguishing "active sensing" from "passive response" requires careful mechanistic dissection

---

## Appendix C: Disclaimer and Limitations

**IMPORTANT**: This framework is offered as a vocabulary for generating hypotheses about physical-molecular relationships, not as a definitive classificatory scheme. The organizational states described are conceptual tools for thinking about multi-level regulation, not rigid categories that natural systems must obey. Specific systems may exhibit characteristics of multiple matrix cells depending on context, and transitions between cells are expected rather than exceptions.

**Type C organization (Physical→Molecular, Constitutive Default)**: This is presented primarily as a theoretical inference from evolutionary principles and in vitro reconstitution experiments, not as an experimentally validated category in modern living organisms. The extent to which contemporary bacteria rely on pure physical-default organization remains an open question.

**Evolutionary narratives**: Claims about early cells relying primarily on physicochemical mechanisms, or about molecular regulation elaborating around physical defaults, are speculative models for generating hypotheses rather than established historical accounts. These narratives should be understood as conceptual foundations for the framework, not as empirically validated evolutionary histories.

**Applicability across organisms**: The framework was developed primarily from *E. coli* and *B. subtilis* literature. Applicability to other bacteria (especially obligate intracellular parasites, cyanobacteria, and archaea) requires systematic testing.
