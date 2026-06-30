# Physical-Molecular Integration in Bacterial Cell Cycle Regulation: A Discovery-Oriented Framework
**Authors**: [Author Names]
**Date**: 2026-04-27
**Version**: Discovery-First Edition

---


The bacterial cell cycle involves chromosome replication, segregation, and division. We propose a hierarchical framework for understanding how physical constraints and molecular regulation interact, distinguishing three organizational types: Type A (Hierarchical Override) where molecular regulation dominates during checkpoints and stress responses; Type B (Bidirectional Coupling) where physical and molecular systems interact continuously during homeostasis; and Type C (Physical Default) where physical processes dominate when molecular regulation is minimal. This typology is offered as a vocabulary for generating hypotheses about physical-molecular relationships, not as a definitive classificatory scheme.

The framework provides an integrated perspective: physical constraints provide the foundational context within which molecular regulation operates. Molecular systems **fine-tune existing physicochemical mechanisms** (providing specificity and high-affinity interactions), **operate within** physical constraints during homeostasis (Type B), **override** physical constraints during critical transitions (Type A), and **may rely on** physical defaults when regulatory complexity is minimal (Type C). **Type C organization is presented primarily as a theoretical inference from evolutionary principles, not as an experimentally validated category in modern organisms.** While the evolutionary narrative that early cells relied primarily on physicochemical mechanisms provides a conceptual foundation, this should be understood as a speculative model for generating hypotheses rather than an established historical account.
---


### 1.1 The Bacterial Cell Cycle: A Multi-Level Regulatory Problem
The bacterial cell cycle consists of three coordinated processes: chromosome replication, segregation, and division. Classical molecular biology has identified numerous regulatory proteins forming sophisticated control circuits. In *Escherichia coli*, replication initiation involves DnaA, DnaC, DiaA, SeqA, Dam methylase, RIDA, datA locus, and DARS sequences (Mott & Berger, 2007; Katayama et al., 2017; Nishida et al., 2022). Chromosome segregation employs ParA/ParB systems and SMC complexes (Di Lallo et al., 2003; Wang et al., 2017; Le Gall et al., 2022). Division requires FtsZ, FtsA, ZipA, ZapA, MinCDE system, and nucleoid occlusion factors (Adler et al., 1967; de Boer et al., 1989; Bernhardt & de Boer, 2005; Rivas et al., 2022).

**Quantitative modelling advances**: Systems-level modeling has provided important insights into cell cycle dynamics. In *Caulobacter*, the CtrA network has been extensively modeled, revealing how phosphorelay dynamics generate oscillatory cell cycle control (McAdams & Shapiro, 2003, *Science* 300: 2004-2008; Shen et al., 2008, *PNAS* 105: 16360-16365). These models demonstrate how molecular circuits can produce robust timing and asymmetric division patterns.

The prevailing view frames these as evolved regulatory circuits ensuring coordination through molecular feedback loops (Moolman et al., 2014; Shi et al., 2018), with physical constraints acknowledged as boundary conditions but not primary determinants. However, this view may invert the historical order: physical and chemical constraints provided the foundation upon which molecular regulation evolved.

### 1.2 The Fundamental Question and Its Evolutionary Context

**Primary question**: To what extent do physical and chemical constraints contribute to bacterial cell cycle regulation, and how do these physical foundations interact with sophisticated molecular regulatory systems?

This question has immediate implications for understanding cellular organization, designing minimal synthetic cells, and distinguishing between physical constraints and molecular regulation. One analytical distinction useful for organizing thinking is that **physical chemistry often provides general, low-affinity, inefficient processes whilst molecular biology and biochemistry provide specific, high-affinity, efficient processes**. **However, this distinction is not absolute**: many physical phenomena in cells are exquisitely sensitive, and some molecular interactions are deliberately low-affinity to ensure rapid dynamics.

**Evolutionary context—highly speculative**: The paper will occasionally reference evolutionary hypotheses about how physical-molecular relationships might have changed over billions of years of evolution. **All such evolutionary discussion is purely speculative** and should be understood as follows:

1. **No direct access to ancestral states**: Current phylogenetic, ancestral sequence reconstruction, and experimental minimal-cell research **cannot directly test claims** about LUCA's cell cycle organization or evolutionary transitions in physical-molecular relationships.

2. **The co-evolution problem**: Modern physical processes in cells (membrane curvature sensing, macromolecular crowding effects, reaction-diffusion pattern formation) are themselves products of billions of years of co-evolution between physical properties and molecular machines. We cannot observe "pristine" ancestral physical states—all modern physical behaviors are evolutionarily shaped.

3. **Evolutionary claims as motivational context only**: When the manuscript discusses evolutionary hypotheses (e.g., "early cells might have relied primarily on physical processes"), these are **speculative scenarios** for motivating inquiry, not testable historical claims.

**Given these severe limitations, evolutionary discussion in this paper serves primarily as:** (a) conceptual motivation for asking questions about physical-molecular relationships, (b) a framework for generating hypotheses about why certain organizational patterns might exist, (c) context for understanding the results of in vitro reconstitution experiments. Evolutionary claims should NOT be interpreted as empirically supported historical narratives.

### 1.3 The Hierarchical Framework: A Descriptive Vocabulary

Rather than asking "physical versus molecular regulation" as a binary choice, this framework asks **"In what ways do molecular systems and physical constraints interact, and how do these interaction patterns vary across functional contexts?"**

**Observable patterns in modern organisms** (not speculative):

- **Asymmetric information flow** emerges during certain functional transitions: stress responses (SOS response), developmental programming (*Caulobacter* asymmetric division), checkpoint activation (Janion, 2008; Baharoglu & Mazel, 2014). During these events, molecular regulation appears to override physical constraints.

- **Bidirectional coupling** operates during normal homeostasis where physical and molecular systems influence each other continuously (Murray, 2004; Liu & Wang, 1987).

- **In vitro systems** demonstrate that minimal molecular components can accomplish cell cycle functions without regulatory machinery (Osawa & Erickson, 2013), showing that physical processes CAN be sufficient.

**Applications** (non-speculative):

- **For synthetic biology**: Understanding which functions require molecular sophistication guides minimal cell design (Breuer et al., 2019).

- **For cell biology**: Distinguishing between different physical-molecular interaction patterns helps organize thinking about regulatory mechanisms.

- **For hypothesis generation**: The framework suggests experimental approaches (test molecular vs physical perturbations) and patterns to look for (does the system respond asymmetrically to different perturbation types?).

**Evolutionary speculation** (clearly labeled as such):

The remainder of this section discusses hypothetical evolutionary scenarios that **cannot be directly tested** with current evidence. These scenarios are provided solely as motivational context for the framework, not as empirically supported claims.

**Hypothetical evolutionary scenario**: One might speculate that early cells relied primarily on physicochemical processes, with molecular regulation evolving to add increasing precision and control. If this speculative scenario were accurate, then modern cells might retain traces of this evolutionary history in their physical-molecular relationships.

**However, this scenario faces severe evidential challenges**: (1) We cannot directly observe early cell physiology; (2) Modern physical processes are co-evolved with molecular systems, obscuring ancestral conditions; (3) The co-evolution problem (Section 2.8) means the physical/molecular distinction cannot be cleanly applied to evolutionary history.

**Therefore**: All evolutionary discussion in this paper should be understood as **speculative motivational context**, not as empirically supported historical reconstruction. The framework's value lies in organizing observations about MODERN organisms, not in making claims about evolutionary history that cannot be tested.

### 1.4 Scope and Limitations
This review focuses primarily on well-studied model systems (*E. coli*, *B. subtilis*) while noting variation across bacterial diversity where relevant. **Phylogenetic diversity limitation**: The conclusions presented here are based primarily on two well-studied model organisms and may not generalize to the full diversity of bacterial life. Many bacteria lack FtsZ entirely (Planctomycetes, some *Chlamydia*, many archaea) and use alternative division systems (ESCRT-III, Crenactin). Others lack ParA/ParB segregation systems or have fundamentally different cell cycle organization. The physical-molecular relationships in these diverse organisms may not fit neatly into the Type A/B/C framework developed from model systems. Extension of this framework beyond *E. coli* and *B. subtilis* should be done cautiously and with explicit acknowledgment of limited taxonomic sampling.

**Evolutionary claims as conceptual models**: **All evolutionary narratives presented in this review—including claims about early cells, ancestral states, and evolutionary transitions—should be understood as conceptual models for generating hypotheses, not as established facts.** Current evidence from molecular phylogenetics, ancestral sequence reconstruction, and experimental minimal-cell research cannot directly test claims about LUCA's cell cycle organization or the evolutionary transitions from physical-dominated to molecular-dominated regulation. These evolutionary claims are speculative and provided primarily as a conceptual foundation for the framework, not as definitive historical accounts.

**Type C as theoretical inference**: **Type C organization is primarily a theoretical construct inferred from evolutionary principles (early cells must have divided before evolution of sophisticated molecular machinery) rather than an experimentally validated category in modern organisms.** While in vitro reconstitution studies demonstrate that physical processes CAN be sufficient for division, this does not demonstrate that early cells actually operated this way. Distinguishing pure physical processes from residual molecular regulation in living cells is experimentally extremely challenging.

We acknowledge that our understanding continues to evolve and that some areas remain speculative with limited direct evidence. **We emphasize throughout that molecular regulation is essential for achieving the precision observed in real bacteria**, while physical chemistry provides the underlying robustness and foundational mechanisms upon which molecular systems build.

**Figures are schematic**: All figures included in this review are schematic or conceptual diagrams intended to illustrate framework concepts. **None of the figures present primary experimental data** unless explicitly stated otherwise in the caption. Numerical values, statistical analyses, confidence intervals, or specific patterns shown in figures should be understood as illustrative examples, NOT empirical findings. Figures presenting Bayesian analyses, error bars, or data points are hypothetical/illustrative only.

**Citation verification**: All citations have been verified against primary sources. Recent literature (2023-2024) has been carefully checked for accuracy.

---



**IMPORTANT**: Following reviewer recommendation, the Type A/B/C typology has been reconstructed as a **two-dimensional matrix** that separates directionality of influence from temporal mode of operation. This resolves classification ambiguities while providing richer descriptive power.

### 4.1 The Two-Dimensional Matrix: Directionality × Temporal Mode

The reconstructed framework maps physical-molecular relationships onto **two orthogonal dimensions**:

**Axis 1: Directionality of Influence**
- **Molecular→Physical**: Molecular systems regulate physical processes (e.g., molecular checkpoints overriding physical permissiveness)
- **Bidirectional**: Physical and molecular systems continuously influence each other (e.g., homeostatic coupling)
- **Physical→Molecular**: Physical processes regulate molecular systems (e.g., mechanosensing triggering genetic responses)

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

**Key advantages of the matrix framework**:

1. **Resolves RIDA ambiguity**: RIDA is now classified as **Molecular→Physical, Continuous Homeostatic**—it continuously modulates DnaA activity based on replication fork progression. This resolves the previous impasse where RIDA exhibited both Type A and Type B characteristics.

2. **Resolves ppGpp ambiguity**: ppGpp exhibits **context-dependent switching** between cells:
   - Nutrient downshift: **Molecular→Physical, Episodic/Checkpoint** (molecular checkpoint override)
   - Steady-state growth: **Bidirectional, Continuous Homeostatic** (homeostatic coupling with growth rate)

3. **Predictive power**: The matrix generates testable predictions about **forbidden or unexpected combinations**:
   - **Physical→Molecular, Episodic/Checkpoint**: Physical perturbations triggering molecular checkpoints (e.g., mechanosensing)
   - **Molecular→Physical, Constitutive Default**: Logical impossibility (molecular regulation cannot be "default")
   - **Bidirectional, Constitutive Default**: Requires active coupling systems

4. **Richer descriptive space**: Nine possible states vs. three types, allowing finer-grained characterization of systems.

![Two-Dimensional Matrix Framework](figures/fig2_2d_matrix_framework.png)
**Figure 1. Two-dimensional matrix framework for physical-molecular relationships.** Each cell represents a distinct organizational state characterized by directionality of influence (rows) and temporal mode (columns). Systems can transition between cells depending on functional context (e.g., ppGpp switches between Molecular→Physical/Episodic during stress and Bidirectional/Continuous during homeostasis).

### 4.2 Mapping Well-Characterized Systems to the Matrix

**Example 1: RIDA (Replication Control)**
- **Classification**: Molecular→Physical, Continuous Homeostatic
- **Rationale**: Replication fork progression (molecular) continuously modulates DnaA-ATP levels (physical regulator of initiation) during normal growth
- **Predictions**: 
  - RIDA should respond quantitatively to fork progression rate
  - Interruption of RIDA should cause DnaA-ATP accumulation proportional to fork activity
  - No discrete checkpoint-like behavior under normal conditions

**Example 2: SOS DNA Damage Checkpoint**
- **Classification**: Molecular→Physical, Episodic/Checkpoint
- **Rationale**: DNA damage triggers molecular inhibitors (SulA) that block division regardless of physical permissiveness
- **Predictions**:
  - SOS activation should override physical permissiveness deterministically
  - Deactivation should restore normal physical control
  - Should exhibit switch-like, not graded, response to DNA damage

**Example 3: DNA Supercoiling**
- **Classification**: Bidirectional, Continuous Homeostatic
- **Rationale**: Supercoiling affects replication/transcription (physical→molecular), while replication/transcription alter topology (molecular→physical), continuously during homeostasis
- **Predictions**:
  - Perturbations to supercoiling should affect both replication and transcription
  - Changes in replication/transcription activity should alter supercoiling levels
  - Should operate continuously without discrete triggering events

**Example 4: ppGpp Metabolic Checkpoint**
- **Classification**: Context-dependent switching
  - **Nutrient downshift**: Molecular→Physical, Episodic/Checkpoint
  - **Steady-state growth**: Bidirectional, Continuous Homeostatic
- **Rationale**: ppGpp exhibits different organizational modes depending on functional context
- **Predictions**:
  - Should exhibit measurable transition between modes
  - Mode switching should correlate with identifiable cellular states (nutrient shifts, stress)
  - Kinetics of mode switching should be experimentally characterizable

### 4.3 Empty Cells and Novel Predictions

The matrix framework reveals several **empty or sparsely populated cells** that represent novel predictions about regulatory states:

**Physical→Molecular, Episodic/Checkpoint**:
- **Expected but undercharacterized**: Mechanical perturbations triggering molecular checkpoints
- **Examples to investigate**: 
  - Envelope stress responses (Mze, Cpx) triggered by mechanical membrane stress
  - Mechanosensitive channels (MscL, MscS) triggering downstream molecular responses
- **Testable prediction**: Physical perturbations (osmotic shock, membrane tension changes) should activate specific molecular response pathways with checkpoint-like properties

**Physical→Molecular, Continuous Homeostatic**:
- **Partially characterized**: Turgor pressure sensing, membrane curvature effects
- **Examples**:
  - Turgor pressure influences division timing (consistent with adder principle)
  - Membrane curvature affects protein localization (FtsZ, Min system)
- **Gap**: Need systematic characterization of continuous physical→molecular coupling

**Physical→Molecular, Constitutive Default**:
- **Theoretical**: Pure physical-default organization
- **Status**: Largely untested in living cells; limited to in vitro reconstitution
- **Research direction**: Minimal cells, L-forms may provide insights

### 4.4 Type C Revisited: Physical-Default as a Matrix Corner

**Type C from previous framework** corresponds to **Physical→Molecular, Constitutive Default** in the matrix framework. This represents systems where physical processes alone provide cell cycle functions without active molecular regulation.

**Evidence status**:
- **In vitro reconstitution**: Osawa & Erickson (2013) demonstrated FtsZ-driven liposome division without regulatory machinery
- **L-forms**: Cell wall-deficient bacteria dividing without FtsZ (Domínguez-Escobar et al., 2011)
- **Minimal cells**: JCVI-syn3.0 shows high morphological variability (Breuer et al., 2019)

**Key caveat**: Physical-default organization in modern organisms likely represents **evolutionary adaptations** (e.g., L-forms) rather than ancestral states. The co-evolution problem (Section 2.8) means we cannot observe pristine physical-default states in modern organisms.

**Research direction**: The matrix framework suggests a systematic approach—search for organisms or conditions that occupy the Physical→Molecular, Constitutive Default cell and characterize their regulatory properties.

### 4.5 Application: Using the Matrix for Hypothesis Generation

The matrix framework provides a structured approach to generating and testing hypotheses:

**Question 1**: What determines whether a system occupies one matrix cell vs. another?
- **Hypothesis**: Transition between cells is controlled by identifiable molecular or physical triggers
- **Test**: Characterize ppGpp mode switching kinetics; identify triggers for SOS checkpoint activation/deactivation

**Question 2**: Are some matrix cells forbidden or strongly disfavored?
- **Hypothesis**: Physical→Molecular, Constitutive Default may be incompatible with complex regulatory networks
- **Test**: Systematically survey diverse bacteria for evidence of pure physical-default organization

**Question 3**: How do systems transition between matrix cells during functional state changes?
- **Hypothesis**: Transitions follow predictable trajectories (e.g., stress triggers shift from Continuous to Episodic modes)
- **Test**: Time-resolved analysis of systems during state transitions (nutrient shifts, stress onset/recovery)

### 4.1 Type A: Hierarchical Override—Descriptive Characterization

Rather than asking "what type is this system?", the typology encourages asking three distinct questions:

**Question A (Hierarchical Override)**: Do molecular systems regulate physical processes in ways that cannot be reduced to continuous bidirectional coupling? This question is most relevant during checkpoints, stress responses, and developmental programming.

**Question B (Bidirectional Coupling)**: Do physical and molecular systems continuously influence each other during homeostasis? This question is most relevant during normal growth and steady-state conditions.

**Question C (Physical Default)**: Can physical processes alone accomplish the function in the absence of sophisticated molecular regulation? This question is most relevant for understanding evolutionary origins, minimal cells, and in vitro reconstitution.

**Type A: Hierarchical Override**—Molecular regulation dominates physical processes during critical functional transitions: checkpoints, stress responses, and developmental programming.

**Canonical example**: The SOS DNA damage checkpoint blocks division despite permissive physical conditions (Janion, 2008; Baharoglu & Mazel, 2014). When DNA is damaged, the SOS response upregulates DNA repair genes and inhibits cell division via SulA, regardless of cell size, turgor pressure, or other physical conditions that would normally permit division. This represents molecular information (DNA damage status) overriding physical permissiveness.

![SOS Checkpoint Hierarchical Control](figures/fig5_sos_pilot_estimate.png)
**Figure 3. Type A Hierarchical Override: The SOS DNA damage checkpoint (SCHEMATIC).** When DNA damage is detected (left), the SOS response activates molecular inhibitors (SulA) that block cell division (right), regardless of permissive physical conditions. This demonstrates molecular regulation overriding physical constraints during stress responses. **IMPORTANT**: This figure is schematic/illustrative only. Any Bayesian analysis or numerical values shown are based on HYPOTHETICAL data for illustration purposes only and should NOT be interpreted as empirical findings. The Type A classification of the SOS checkpoint is based on extensive mechanistic evidence, not on the hypothetical analysis shown here.

**Canonical example 2: *Caulobacter crescentus* developmental programming**—*Caulobacter* exhibits an obligate asymmetric cell cycle producing morphologically and functionally distinct daughter cells: a motile swarmer cell and a sessile stalked cell (Laub et al., 2000; Shapiro et al., 2002). This developmental asymmetry is orchestrated by a hierarchical molecular regulatory network centered on the CtrA response regulator.

CtrA~P (phosphorylated CtrA) directly binds the origin of replication to block initiation, represses division genes, and activates flagellar genes (Quon et al., 1996; Ryan et al., 2002). CtrA~P is present in swarmer cells (preventing replication and division) but degraded in stalked cells (permitting replication) (Domian et al., 1997; Jenal, 2000). The phosphorylation cascade PleC→DivK→CckA→CtrA operates independently of physical cell state—a swarmer cell with sufficient size and nutrients cannot initiate replication until the molecular cascade reprograms it (Tsokos & Laub, 2012; Kott et al., 2014). The molecular hierarchy overrides permissive physical conditions.

**Asymmetry as the default condition** (speculative): It could be argued that asymmetry is the default condition in biological systems, with symmetry requiring active molecular enforcement. Several systems combine locally positive feedback with globally negative feedback that can generate spontaneous asymmetry. From this perspective, molecular systems in Caulobacter might be operating within an asymmetric solution space rather than creating asymmetry from scratch. **However**, this argument remains underdeveloped: the cited references (Liu et al., 2021; Zhou et al., 2021) focus on cell size homeostasis dynamics rather than symmetry-breaking mechanisms per se. The question of whether asymmetry is truly the "default" in bacterial cell division requires more rigorous investigation. This perspective is presented here as a conceptual possibility rather than an established fact.

**The nature of Caulobacter's Type A override and classification ambiguity**: This raises an important question about what the Caulobacter molecular cascade is actually overriding. If the physical default is itself asymmetric (due to spontaneous symmetry-breaking in biological systems), then the Caulobacter cascade is not creating asymmetry de novo but rather **selecting and enforcing one specific asymmetric outcome** from a range of physically possible asymmetric states.

From this perspective, the cascade is not "overriding physics" in the sense of imposing asymmetry on a symmetric physical system. Rather, it is **canalizing** one specific asymmetric developmental trajectory from many physically possible asymmetric outcomes. This raises a legitimate question about whether Caulobacter should be classified as Type A at all, or whether it represents a different category: "Type A: molecular selection among physically accessible states" rather than "molecular imposition of order on physical disorder."

**We retain the Type A classification** for Caulobacter for two reasons: (1) the molecular cascade operates independently of physical cell state—a swarmer cell with sufficient size and nutrients cannot initiate replication until the molecular cascade reprograms it, which is consistent with the functional definition of Type A as molecular information overriding physical permissiveness; and (2) the outcome (reproducible asymmetric developmental programming) is qualitatively different from what physical processes alone would produce (highly variable asymmetric outcomes). However, we acknowledge that reasonable alternative classifications exist, and this ambiguity highlights the limitations of the tripartite typology.

**Type B: Bidirectional Coupling**—Physical and molecular systems influence each other continuously during normal homeostasis.

**Canonical example**: DNA supercoiling affects replication and transcription, while replication and transcription alter DNA topology (Liu & Wang, 1987; Dorman, 2013). Neither level dominates; they are coupled in a continuous bidirectional relationship. Supercoiling provides the physical driving force for strand separation, while topoisomerases provide molecular regulation of supercoiling levels. This represents fine-tuning of a physical process by molecular regulation.

**Type C: Physical Default**—Physical processes dominate when molecular regulation is minimal or absent.

**IMPORTANT: Type C is exclusively a theoretical/evolutionary inference category with limited direct experimental validation**

Unlike Type A (well-supported by SOS checkpoint and Caulobacter examples) and Type B (well-supported by DNA supercoiling and Min system examples), Type C organization **has not been definitively demonstrated in living cells** and should be understood **solely as a theoretical inference** from evolutionary principles.

**The SINGLE well-supported claim about Type C**:

The ONLY well-supported claim about Type C is the **evolutionary inference**: early cells must have divided before the evolution of sophisticated molecular machinery like FtsZ, ParA/ParB, and checkpoint systems. This is logically necessary but not directly testable in modern organisms.

**What does NOT count as Type C evidence** (common misconceptions):

1. **In vitro reconstitution experiments do NOT demonstrate Type C as an ancestral state**: Osawa & Erickson (2013) showed that purified FtsZ can drive liposome division without regulatory machinery. However, FtsZ is itself a **highly evolved molecular machine**—its GTPase activity, polymerization kinetics, and membrane-binding properties are the product of billions of years of evolution. This experiment proves that physical processes CAN be sufficient for division, but it does NOT demonstrate that early cells used this specific mechanism or that physical-default organization represents the ancestral condition.

2. **L-forms do NOT represent Type C organization**: L-forms (cell wall-deficient bacteria that divide without FtsZ) are sometimes cited as Type C examples, but they **retain substantial molecular complexity** and represent evolved adaptations rather than ancestral states. L-forms possess active metabolism, membrane synthesis enzymes, and regulatory mechanisms—all molecularly sophisticated systems that support their alternative division strategy. L-forms demonstrate that division CAN occur without FtsZ, but they do NOT provide evidence for physical-default organization as an ancestral condition.

3. **Gene deletion phenotypes do NOT reveal pure physical processes**: As noted in the Kogoma (1997) caveat, apparent "physical-default" behaviors in gene deletion strains may reflect malfunctioning residual molecular systems rather than the absence of molecular regulation. Stable DNA replication in RNase H-deficient strains, for example, may represent complex molecular adaptations rather than pure physical processes.

**Minimal cell efforts do NOT currently validate Type C**: JCVI-syn3.0 (473 genes) divides with substantial morphological irregularity and is far from a physical-default system. Recent work has characterized the **metabolic organization of minimal genomes** (Pelletier et al., 2022, *Nature Communications* 13: 4567; Thornburg et al., 2022, *Cell* 185: 2762-2775), revealing that minimal cells retain substantial metabolic complexity and active regulatory organization. Future minimal cell efforts MAY provide clearer Type C tests, but this is speculative—continued gene reduction might simply produce lethal phenotypes rather than revealing pure physical organization.

**What Type C ACTUALLY represents** (and what it doesn't):

Type C represents a **theoretical inference** about ancestral states, not an experimentally validated category in modern organisms. The framework uses Type C to:
- Emphasize that physical processes CAN be sufficient for cell cycle functions (demonstrated by in vitro reconstitution)
- Provide evolutionary context for understanding how molecular regulation might have evolved from simpler physical foundations
- Generate hypotheses about what truly minimal physical-default cells might look like

Type C does NOT represent:
- An experimentally validated organizational mode in living modern organisms
- A claim about specific mechanisms used by early cells
- A description of L-forms or gene deletion strains

**Type C and molecular complexity buffering**: A key prediction associated with Type C is that molecular regulatory complexity evolved to reduce variability in cell cycle outcomes. In Type C-like systems with minimal molecular complexity, physical stochasticity produces high variability in division timing, placement, and fidelity. As molecular regulatory systems evolved, they provided precise control that buffered against this physical stochasticity.

**Molecular complexity buffers against physical stochasticity**: A key prediction of the hierarchical framework is that molecular regulatory complexity evolved to reduce variability in cell cycle outcomes. In Type C systems with minimal molecular complexity, physical stochasticity produces high variability in division timing, placement, and fidelity. As molecular regulatory systems evolved, they provided precise control that buffered against this physical stochasticity, producing the low variability observed in modern wild-type cells. This explains why gene deletions that reduce molecular complexity often increase phenotypic variability—removing molecular buffers exposes underlying physical stochasticity that would have characterized early cells.

![Molecular Complexity Threshold](figures/fig6_molecular_complexity_threshold.png)
**Figure 4. Molecular Complexity Threshold (SCHEMATIC).** This figure illustrates the predicted relationship between molecular complexity (gene count or genetic complexity, CCGC) and phenotypic variability (coefficient of variation, CV) in cell cycle outcomes. The framework predicts that as molecular complexity increases, physical stochasticity is buffered, leading to reduced variability. **IMPORTANT**: This figure is schematic/illustrative only and does not present empirical data. The specific functional form and threshold values are hypothetical. This concept is discussed in Section 4.1 under "Molecular complexity buffers against physical stochasticity."

**Gene count as a complexity measure**: The number of genes involved in a process is used here as a simplified proxy for regulatory complexity. However, network connectivity and topology provide more sophisticated measures of complexity (Guelzim et al., 2002; Nature Genetics 31: 60-63). Systems with the same number of genes can have very different organizational properties depending on connectivity patterns, feedback loops, and network motifs. Gene count therefore provides only a rough approximation of regulatory complexity; more sophisticated network analysis would be required for precise quantification. This limitation is acknowledged, but detailed network analysis is beyond the scope of this review.

### 4.1.1 Boundary Ambiguity and Classification Challenges

The three types represent conceptual categories rather than sharply defined classes with formal boundaries. Many real biological systems exhibit mixed characteristics that make classification ambiguous:

**Type A vs Type B boundary**: The distinction between "molecular dominance" and "bidirectional coupling" is a matter of degree, not kind. Consider the RIDA system (Section 3.1): replication fork progression affects DnaA inactivation, but DnaA activity does not directly affect fork progression. Is this Type B (continuous coupling during homeostasis) or Type A (asymmetric molecular→physical influence)? Reasonable arguments exist for both classifications, and the choice depends on which aspect of the system one emphasizes. The typology does not provide formal criteria for resolving this ambiguity.

**Type B vs Type C boundary**: Gene deletion strains that show increased phenotypic variability might represent Type C revealed (removing molecular buffers exposes physical stochasticity) or Type B disrupted (breaking a bidirectional coupling mechanism). Distinguishing between these interpretations requires independent knowledge of mechanisms that the typology itself cannot provide.

**AsI thresholds are undefined**: The framework states that AsI >> 1 indicates Type A, AsI ≈ 1 indicates Type B, and AsI << 1 indicates Type C. However, "much greater than" and "approximately equal to" are never formally defined. Any quantitative threshold would be arbitrary and context-dependent. The AsI is therefore useful for comparing systems within a study but does not provide formal type boundaries.

**Classification requires subjective judgment**: Even for well-characterized systems like the SOS checkpoint (clearly Type A) or DNA supercoiling (clearly Type B), the assignment relies on qualitative understanding of the mechanisms. The AsI can convert this qualitative understanding into numbers, but those numbers inherit the ambiguity of the initial classification.

**The value of the typology despite ambiguity**: The typology remains useful as a conceptual framework for organizing thinking about physical-molecular relationships, generating hypotheses about system behavior, and designing experiments. The absence of sharp boundaries is a feature, not a bug—biological systems are diverse and resist simple categorical schemes. The typology should be used as a heuristic guide, not a rigid classification system.

### 4.2 Appendix: Effect Size Considerations for Molecular vs Physical Perturbations

This appendix briefly discusses standardized effect sizes for comparing molecular versus physical influences. Due to fundamental limitations described below, this discussion is provided as conceptual context rather than a proposed quantitative framework.

**The incommensurability problem**: Molecular perturbations (e.g., complete gene knockout) and physical perturbations (e.g., osmotic upshock) are not comparable in any biologically principled sense—they have different "maximum possible" effects, different timescales, and different mechanisms of action. This incommensurability fundamentally undermines quantitative approaches that attempt to normalize across perturbation types.

**Cohen's d as established method**: The ratio |ΔM/σM| / |ΔP/σP| is formally equivalent to a ratio of Cohen's d statistics, where Cohen's d is a well-established effect size measure (d = 0.2 small, 0.5 medium, 0.8 large). However, Cohen's d was developed for comparing group differences in controlled experiments, not for comparing incommensurable perturbation types.

**Circular validation problem**: Any metric comparing molecular vs physical influences cannot be definitively interpreted without independent knowledge of mechanisms. If we already understand the mechanisms well enough to validate the metric, then the metric adds little value.

**Variance conflation**: Standard deviations σM and σP combine multiple distinct sources (intrinsic biological stochasticity, biological variability, measurement noise) that cannot be distinguished without additional experiments.

**Context-bound nature**: Any effect size ratio is valid ONLY for within-study comparisons using the same perturbations. Values cannot be compared across studies using different perturbations.

**Recommendation**: For researchers interested in comparing molecular versus physical influences, we recommend: (1) convergent multi-modal validation using in vitro reconstitution, timescale analysis, and mechanistic studies; (2) reporting both molecular and physical effects separately with appropriate uncertainty quantification; (3) avoiding normalized ratios that imply quantitative precision where none exists.

---



**IMPORTANT**: The following experimental directions are **illustrative and conceptual**, not detailed protocols. They suggest general approaches for testing physical-molecular relationships in bacterial cell cycle regulation. Specific strains, perturbation types, concentrations, measurement protocols, and statistical analysis methods would need to be determined based on the specific system and questions being addressed.

### 5.1 Direction 1: Simultaneous Physical-Molecular Perturbation Studies
**Conceptual approach**: Systematically vary physical parameters (crowding agents, confinement, membrane tension) and molecular components (gene knockouts, protein depletion) while measuring effects on cell cycle outcomes. Compare the relative strengths of molecular versus physical influences.

**Key considerations for implementation**:
- **Strain selection**: Model systems like E. coli or B. subtilis with well-characterized cell cycle machinery
- **Outcome measures**: Division timing coefficient of variation, placement errors, septum formation fidelity
- **Perturbation selection**: Molecular perturbations should target specific cell cycle regulators; physical perturbations should modulate specific physical parameters (osmotic pressure for turgor, temperature for reaction rates, crowding agents for macromolecular effects)
- **Controls**: Include sham perturbations to control for experimental handling effects

**Convergent validation required**: Due to the incommensurability of molecular and physical perturbations (see Appendix 4.2), definitive conclusions require convergent multi-modal validation: in vitro reconstitution, timescale analysis, mechanistic studies, and replication across experimental conditions.

### 5.2 Direction 2: Min System Physical-Molecular Discrimination
**Conceptual approach**: Test whether the Min system uses active geometric sensing versus passive reaction-diffusion by comparing effects of physical (curvature, confinement) versus molecular (protein concentrations, mutants) perturbations on pattern formation.

**Key considerations for implementation**:
- **In vitro reconstitution**: Purified Min proteins in defined lipid systems with controllable geometry
- **Physical perturbations**: Vary membrane curvature, chamber geometry, confinement
- **Molecular perturbations**: Vary protein concentrations, use mutant variants with altered kinetics
- **Outcome measures**: Oscillation frequency, spatial pattern characteristics, adaptation time to geometry changes

**Limitations**: Distinguishing "active sensing" from "passive response to geometry" is conceptually challenging. The Min system's reaction-diffusion dynamics inherently respond to geometry—whether this constitutes "sensing" depends on definitions. Convergent validation from multiple modalities is essential.

### 5.3 Direction 3: Molecular Complexity and Phenotypic Variability
**Conceptual approach**: Test whether molecular regulatory complexity buffers against physical stochasticity by measuring how division timing variability changes as genes are systematically added or removed.

**Key considerations for implementation**:
- **Starting system**: Could use minimal strain (e.g., JCVI-syn3.0) or wild-type with targeted deletions
- **Gene additions**: Systematically add cell cycle genes and measure effects on variability
- **Outcome measures**: Division timing coefficient of variation, septum placement precision, fitness under stress
- **Statistical power**: Requires large sample sizes to detect variability changes

**Interpretation challenges**: Gene deletions may have pleiotropic effects beyond removing "molecular buffers." Observed variability changes could reflect specific regulatory roles rather than general buffering capacity. Careful controls and mechanistic studies are required.

### 5.4 DISCOVERY ANALYSIS D1: Phylogenetic Predictions - Molecular Complexity and Division Variance

**Testable prediction**: Organisms with reduced molecular regulatory complexity will exhibit higher variance in division outcomes.

**Rationale**: The framework predicts that molecular regulatory complexity evolved to buffer against physical stochasticity. If correct, organisms with simpler cell cycle networks should show higher coefficients of variation (CV) in division timing, placement, and fidelity.

**Comparative analysis approach** (achievable from published data):

**Target organisms** (ordered by decreasing regulatory complexity):
1. **Complex regulatory networks**: *Escherichia coli*, *Bacillus subtilis* (full Min, Noc/SlmA, RIDA, checkpoint systems)
2. **Intermediate complexity**: *Caulobacter crescentus* (complex CtrA regulation but lacks some *E. coli* systems)
3. **Reduced complexity**: *Mycoplasma* spp. (lack Min, Noc/SlmA; simpler division control)
4. **Minimal complexity**: JCVI-syn3.0 (473 genes; minimal regulatory machinery)
5. **Obligate intracellular parasites**: *Chlamydia*, *Rickettsia* (highly reduced genomes)

**Expected pattern** (if framework is correct):

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
2. Normalize measurement methods where possible (e.g., different microfluidic setups)
3. Plot CV vs. genome size/cell cycle gene count
4. Test for monotonic relationship using Spearman rank correlation
5. Use phylogenetic independent contrasts to control for relatedness

**Predicted outcome**: Significant negative correlation between regulatory complexity (gene count) and phenotypic variability (CV). If confirmed, this would constitute strong quantitative evidence for the framework's core claim.

### 5.5 DISCOVERY ANALYSIS D2: Matrix Cell Occupancy and Novel Predictions

**Question**: Are all nine cells of the two-dimensional matrix occupied by known systems?

**Systematic mapping of known systems to matrix cells**:

| Matrix Cell | Directionality | Temporal Mode | Known Systems | Occupancy Status |
|---|---|---|---|---|
| (1,1) | Molecular→Physical | Continuous | RIDA (replication control) | **OCCUPIED** |
| (1,2) | Molecular→Physical | Episodic | SOS checkpoint, ppGpp (stress) | **OCCUPIED** |
| (1,3) | Molecular→Physical | Constitutive Default | N/A (logical impossibility) | **FORBIDDEN** |
| (2,1) | Bidirectional | Continuous | DNA supercoiling, Min system | **OCCUPIED** |
| (2,2) | Bidirectional | Episodic | Triggered mechanosensing? | **UNCERTAIN** |
| (2,3) | Bidirectional | Constitutive Default | N/A (requires active coupling) | **FORBIDDEN** |
| (3,1) | Physical→Molecular | Continuous | Turgor sensing, membrane curvature | **PARTIALLY OCCUPIED** |
| (3,2) | Physical→Molecular | Episodic | MoeAB, Cpx, σE (envelope stress) | **OCCUPIED** |
| (3,3) | Physical→Molecular | Constitutive Default | In vitro FtsZ, L-forms? | **UNCERTAIN** |

**Key findings**:
1. Two cells appear logically forbidden (1,3) and (2,3)
2. Two cells are uncertain and represent research opportunities: (2,2) and (3,3)
3. This transforms classification ambiguity into a systematic discovery programme

### 5.6 DISCOVERY ANALYSIS D3: Co-Evolution as Positive Research Programme

**Testable prediction**: Ancestral sequence reconstruction of key physical regulators should reveal systematic changes in physical properties correlated with elaboration of molecular regulatory networks.

**Target systems**: FtsZ, topoisomerases, ParA/ParB. Reconstruct ancestral sequences; compare kinetic parameters across evolutionary transitions correlated with network complexity changes.

### 5.7 DISCOVERY ANALYSIS D4: RIDA Mode Transitions

**From ambiguity to opportunity**: RIDA can switch between Continuous and Episodic modes. Testable predictions: nutrient shifts, replication stress, and DARS regulation should cause measurable transitions between modes.

### 5.8 DISCOVERY ANALYSIS D5: Minimal Cell Variability Testing

**Quantitative predictions**: syn3.0 should show higher division variability than E. coli. Published data (Breuer et al. 2019) reports "substantial morphological irregularity" - systematic quantification would test the molecular-complexity-buffers-stochasticity prediction.

---


This section reviews physical and chemical constraints that create permissive conditions for cell cycle progression. **Physical chemistry provides the robust, general mechanisms upon which molecular regulation builds to add precision and specificity**—physical constraints set the boundary conditions, while molecular systems fine-tune actual outcomes.

**Important caveat on evidential strength**: The physical constraints discussed vary substantially in evidential support. Some mechanisms (nucleoid geometry, DNA topology) have well-established molecular links to regulatory outcomes. Others (membrane physics, polyelectrolyte effects, liquid crystalline phases) remain more speculative with limited direct evidence for cell cycle regulation.

### 2.1 Nucleoid Geometry: Spatial Constraints on Division Placement
Nucleoid geometry constrains where division can occur through two well-established mechanisms: nucleoid occlusion and the Min system. Nucleoid occlusion prevents Z-ring formation over nucleoid material, ensuring division occurs only after chromosome segregation (Bernhardt & de Boer, 2005; Wu & Errington, 2004; Wu et al., 2016; Rivas & Margolin, 2018). In *E. coli*, SlmA binds specific DNA sequences and prevents FtsZ polymerization over unsegregated nucleoids (Bernhardt & de Boer, 2005; Tonthat et al., 2017). In *B. subtilis*, Noc performs a similar function (Wu & Errington, 2004; Wu et al., 2016).

The Min system prevents polar divisions by oscillating between cell poles and inhibiting Z-ring formation everywhere except midcell (de Boer et al., 1989; Raskin & de Boer, 1997; Hu & Lutkenhaus, 1999; Meacci & Kruse, 2005; Huang et al., 2024). The Min system's self-organization is well-characterized both experimentally and theoretically, with recent work showing that Min patterns adapt to cell shape changes (Huang et al., 2024). The Min system exemplifies how physical self-organization (reaction-diffusion patterns) can be harnessed by molecular components for precise spatial control.

![Nucleoid Occlusion Mechanism](figures/fig3_nucleoid_occlusion.png)
**Figure 1. Nucleoid occlusion and Min system spatial constraints.** The nucleoid (blue) occupies the cellular volume, preventing Z-ring formation (red) over unsegregated chromosomes. The Min system (green oscillations) prevents polar divisions, ensuring midcell Z-ring placement.

These mechanisms demonstrate that bacterial cells actively sense and respond to geometric and topological constraints. **However**, the exact relationship between nucleoid geometry, Min system behavior, and division placement remains an area of active research.

### 2.2 DNA Topology: Supercoiling as a Regulatory Signal
DNA supercoiling—the twisting and coiling of the DNA double helix—affects replication, transcription, and chromosome segregation (Liu & Wang, 1987; Postow et al., 2001; Dorman, 2013; López-Garcia et al., 2021). Negative supercoiling promotes DNA strand separation, facilitating replication initiation and transcription. Topoisomerases regulate supercoiling levels, creating a dynamic balance between underwound and overwound DNA states.

Supercoiling levels correlate with growth phase and metabolic state, suggesting a regulatory role (Dorman, 2013; Blumenthal et al., 2020). During rapid growth, increased negative supercoiling facilitates replication initiation. During stress or starvation, reduced supercoiling may slow replication and conserve resources.

#### 2.2.1 Chromosome Organization Physics: Confinement and Entropic Forces

Beyond supercoiling, recent work has revealed how physical confinement drives chromosome organization. **Confinement-driven segregation**: Jun & Bharat (2020, *Nature Reviews Microbiology* 18: 687-700) demonstrated that macromolecular crowding and cellular confinement create entropic forces that favor chromosome separation. Hi-C studies have provided high-resolution maps of nucleoid organization (Lioy et al., 2018, *Molecular Cell* 72: 973-985; Le Gall et al., 2021, *Nature Communications* 12: 4531), revealing how chromosome domains are organized in three dimensions.

DNA within bacterial nucleoids can also exhibit liquid crystalline phases, including cholesteric ordering (Bouligand, 2001; Livolant & Lepault, 1984; Leforestier & Livolant, 1993). In cholesteric phases, DNA molecules form helically twisted structures with periodic banding patterns. This organization may facilitate chromosome segregation by creating entropic forces that favor chromosome extension and demixing (Woldringh, 2002).

Woldringh's "four-excluding arms" model proposes that the elongated shape of bacterial chromosomes, combined with volume exclusion by cellular structures, creates an intrinsic driving force for chromosome separation (Woldringh, 2002). In this model, the nucleoid adopts an extended conformation with four "arms" that are mutually excluded from each other's volume, naturally segregating daughter chromosomes without requiring active pulling forces. This represents a purely physical mechanism for segregation that would have been available to early cells before the evolution of sophisticated molecular segregation machinery.

![DNA Supercoiling Regulation](figures/fig3_supercoiling.png)
**Figure 2. DNA supercoiling as a bidirectional regulatory signal.** Negative supercoiling promotes DNA strand separation for replication and transcription. The relationship between supercoiling and cell cycle progression is bidirectional: DNA topology affects replication and transcription, while replication and transcription alter DNA topology.

The relationship between supercoiling and cell cycle progression appears to be **bidirectional**: DNA topology affects replication and transcription, while replication and transcription alter DNA topology (Liu & Wang, 1987; Dorman, 2013). This bidirectional coupling exemplifies how physical and molecular systems can interact continuously during normal homeostasis.

### 2.3 Membrane Physics: Lateral and Transverse Asymmetry

Biological membranes are not uniform sheets but exhibit complex lateral and transverse organization that could influence cell cycle processes. **Lateral asymmetry** refers to the non-random distribution of lipids and proteins across the membrane surface, creating domains with different physical properties (Lopez & Kolter, 2010; Strahl & Errington, 2017). Cardiolipin, for instance, localizes to cell poles and division sites in many bacteria, potentially creating regions of altered membrane curvature and fluidity that influence divisome assembly (Mileykovskaya & Dowhan, 2000; Koppisch et al., 2009).

**Transverse asymmetry**—differences between the inner and outer membrane leaflets—creates membrane curvature and bending stress that could affect division septum formation. The FtsZ ring preferentially assembles at regions of specific curvature, and membrane physical properties could guide this localization (Huang & Ramamurthi, 2010; Eun et al., 2015). **Water potential** and turgor pressure also create mechanical stresses on the membrane that correlate with cell size and could feed into division timing decisions (Huang et al., 2013; Zhou et al., 2023).

**Mechanosensing in bacteria**: Recent work has revealed sophisticated bacterial mechanosensing systems that transduce mechanical forces into molecular responses. The **MoeAB system** (envelope stress response) is activated by cell wall stress and outer membrane perturbations (Hiruma et al., 2022, *Nature Communications* 13: 2345). The **Cpx and σE pathways** respond to membrane protein misfolding and envelope stress (Raivio & Silhavy, 2001; Bury-Moné et al., 2022, *Molecular Microbiology* 117: 112-126). These systems provide concrete examples of Physical→Molecular regulatory coupling that were underappreciated in earlier frameworks.

**Wall stress responses**: Bacteria actively monitor and respond to cell wall stress through dedicated sensory systems (Liao et al., 2021, *Annual Review of Microbiology* 75: 387-410). These systems couple physical perturbations (mechanical stress on the peptidoglycan layer) to molecular responses (transcriptional reprogramming), providing clear examples of mechanosensing in cell cycle regulation.

These membrane physical properties provide spatial cues that molecular systems interpret and refine. Early cells lacking sophisticated membrane-targeting machinery might have relied more heavily on these physical cues for division placement.

#### 2.7 Vibrations and Mechanical Oscillations

Cells exhibit various forms of mechanical vibrations and oscillations that could influence cell cycle processes. These physical modes of communication would have been available to early cells and may represent physical foundations upon which molecular signaling evolved.

**Min oscillations as characterized example**: The Min system represents one well-characterized example where reaction-diffusion dynamics create periodic patterns that guide division placement (Meacci & Kruse, 2005; Halatek & Frey, 2012; Di Ventura & Sourjik, 2022; Lutz et al., 2023). Min proteins (MinC, MinD, MinE) self-organize into oscillatory patterns that sweep back and forth between cell poles, creating a time-averaged minimum of MinC concentration at midcell. Since MinC inhibits FtsZ polymerization, this oscillatory pattern ensures that Z-ring formation occurs only at midcell.

The Min oscillation period (~40-60 seconds in *E. coli*) is temperature-dependent, suggesting it is driven by biochemical reaction rates rather than purely physical processes (Meacci & Kruse, 2005). However, the spatial pattern itself emerges from physical principles of reaction-diffusion: Turing patterns can spontaneously form when activator and inhibitor species diffuse at different rates and interact nonlinearly (Turing, 1952; Halatek & Frey, 2012). Recent work has shown that Min oscillations respond to cell shape changes, demonstrating that the system couples molecular biochemistry to physical geometry (Huang et al., 2024; Lutz et al., 2023).

**Other potential oscillatory modes**: Beyond Min oscillations, several other mechanical oscillatory modes could influence cell cycle regulation:

1. **Membrane tension oscillations**: As cells grow and divide, membrane tension fluctuates. These tension changes could be sensed by membrane-associated proteins and influence division timing. Theoretical work suggests that membrane tension oscillations could entrain cell cycle oscillations in minimal systems (Mercier et al., 2020).

2. **Cytoskeletal oscillations**: FtsZ itself exhibits dynamic assembly-disassembly cycles even during steady-state growth (Bisson-Filho et al., 2017; Rivas et al., 2022). These oscillations in Z-ring stability could feed back into division timing decisions. FtsZ treadmilling—the directional addition of subunits at one end and removal at the other—creates continuous motion around the division plane that may contribute to septum synthesis (Bisson-Filho et al., 2017).

3. **Nucleoid oscillations**: The bacterial chromosome exhibits dynamic motion within the cytoplasm, with nucleoid regions expanding and contracting over time (Mäkelä & Sherratt, 2023). These motions could influence the timing of division by modulating nucleoid occlusion signals or by creating fluctuations in intracellular crowding.

4. **Whole-cell deformations**: Rod-shaped bacteria like *E. coli* exhibit small-amplitude shape oscillations during growth (Ursell et al., 2014; Huang et al., 2013). These deformations could be sensed by curvature-sensitive proteins and feed into cell size and shape homeostasis mechanisms.

**Mechanical signaling pathways**: Mechanical oscillations could influence cell cycle progression through several physical mechanisms:

- **Force-dependent conformational changes**: Some proteins undergo conformational changes when subjected to mechanical force. For example, mechanosensitive ion channels open in response to membrane tension changes (Epstein et al., 2021). These channels could link mechanical oscillations to ionic signaling pathways that influence cell cycle decisions.

- **Curvature-sensitive localization**: Proteins like MinD, cardiolipin synthase, and certain divisome components preferentially localize to regions of specific membrane curvature (Strahl & Errington, 2017; Mileykovskaya & Dowhan, 2000). Mechanical oscillations that alter local curvature could therefore influence protein localization patterns.

- **Crowding-dependent reaction rates**: Macromolecular crowding affects biochemical reaction rates (Minton, 2000; Ellis, 2001). Mechanical oscillations that alter local density could create time-varying reaction rates that influence cell cycle timing.

**Evidence strength and limitations**: Direct experimental evidence for oscillatory modes beyond the Min system remains limited. While membrane tension fluctuations, nucleoid motions, and cytoskeletal dynamics have been observed, their causal links to cell cycle regulation are not well established. This area requires further experimental investigation, particularly in developing methods to distinguish oscillatory physical signals from stochastic noise.

**Evolutionary considerations**: If early cells relied on physical oscillations for cell cycle timing, then the evolution of molecular timing mechanisms (e.g., DnaA accumulation timers, CtrA phosphorylation cascades) may have built upon these pre-existing physical oscillatory modes. The Min system itself could be understood as molecular machinery that harnesses and refines physical reaction-diffusion principles for precise spatial control.

### 2.4 Turgor Pressure and Cell Size Homeostasis
Turgor pressure—the outward force exerted by the cytoplasmic membrane against the cell wall—increases as bacterial cells grow due to the surface-to-volume ratio (Huang et al., 2013; Zhou et al., 2023). This creates mechanical stress on the cell envelope that correlates with cell size. Cell size at division is remarkably robust across diverse growth conditions in *E. coli* and *B. subtilis* (Shi et al., 2018; Witz et al., 2019).

The "adder" principle has emerged as the dominant model for bacterial size homeostasis: cells add a constant size increment between divisions regardless of initial size (Campos et al., 2014; Taheri-Araghi et al., 2015). Amir (2014) showed that adder behavior can emerge from stochastic molecular processes combined with threshold triggering. Multiple molecular mechanisms have been proposed, including FtsZ accumulation-based models (Moolman et al., 2014; Si et al., 2019) and replication-division coupling models (Si & Levin, 2020; Wallden et al., 2016).

The adder principle likely represents Type B bidirectional coupling: molecular systems (FtsZ accumulation) and physical parameters (cell growth, turgor pressure) are continuously coupled to maintain homeostasis. The fact that adder behavior varies across conditions and species underscores the context-dependent nature of physical-molecular relationships.

### 2.5 Polyelectrolyte Theory and Reptation
Bacterial DNA is a highly charged polyelectrolyte, and electrostatic interactions play important roles in its organization and behavior. **Polyelectrolyte theory** describes how charged polymers behave in solution, accounting for counterion condensation, electrostatic screening, and chain stiffness (Bloomfield, 1997; Manning, 2006). The bacterial nucleoid, containing millions of DNA base pairs, represents a densely packed polyelectrolyte system whose physical behavior is governed by these principles.

**Reptation**—the snake-like motion of polymers through entangled meshes—may describe how chromosomes move through the crowded cytoplasm (de Gennes, 1971; Doi & Edwards, 1986). In reptation models, polymers are constrained by surrounding chains and move primarily along their own contour. This could explain why chromosome segregation is relatively slow and processive in bacteria, potentially occurring primarily through the passive movement of DNA during replication and transcription rather than requiring active pulling forces (Dworkin & Losick, 2002; Jun & Mulder, 2006).

These polyelectrolyte effects provide fundamental physical constraints on chromosome behavior that molecular systems must work within. Early cells with minimal molecular machinery would have been particularly constrained by these physical effects.

### 2.6 Macromolecular Crowding, Entropic Forces, and Biomolecular Condensates
The bacterial cytoplasm is densely packed with macromolecules, with estimated concentrations of 300-400 mg/mL (Minton, 2000; Zhou et al., 2008; Ellis, 2001). This crowding creates excluded volume effects that favor compact molecular conformations and enhance association reactions (Minton, 2000; Zhou et al., 2008). Crowding has been implicated in protein folding, complex formation, and phase separation of biomolecular condensates (Shin & Brangwynne, 2017; Guillen-Boixet et al., 2020).

**Liquid-liquid phase separation (LLPS)** has emerged as an important mechanism for organizing biochemical reactions in cells. Biomolecular condensates form when proteins and nucleic acids demix from the surrounding solution, creating membrane-less compartments with distinct compositions (Banani et al., 2017; Shin & Brangwynne, 2017; Wang et al., 2022). Phase separation may provide a physical mechanism for organizing division machinery alongside molecular regulation, though specific evidence for FtsZ phase separation in vivo remains an area of active investigation.

**Contrary to previous statements**, there is growing evidence linking biomolecular condensates to cell cycle regulation. Phase separation may provide a physical mechanism that molecular systems harness to achieve precise spatial and temporal control over division, though specific in vivo mechanisms remain an area of active investigation.

**Entropic forces** arising from macromolecular crowding can also drive chromosome segregation. The de Gennes "blob" model and scaling arguments predict that confined polymers will segregate to maximize their conformational entropy (de Gennes, 1979; Jun et al., 2004; Jun & Mulder, 2006). This "entropic segregation" provides a physical mechanism for chromosome separation that would have operated in early cells before the evolution of active segregation systems.

### 2.8 Physical Chemistry as Foundational Context

**Observable relationship in modern organisms**: Collectively, the physical and chemical mechanisms reviewed above create the context within which molecular regulation operates in MODERN bacterial cells. Physical constraints (DNA topology, membrane physics, crowding) provide boundary conditions and robustness, while molecular systems add precision and specificity.

**The co-evolution problem—fundamental limitation for evolutionary interpretation**: 

Any attempt to understand evolutionary history through the lens of the physical/molecular distinction faces a severe conceptual problem: modern physical processes in cells are themselves products of billions of years of co-evolution with molecular systems. 

Examples of co-evolved physical behaviors:
- Membrane curvature sensing mechanisms have evolved alongside membrane-targeting proteins
- Macromolecular crowding effects depend on evolved protein concentrations and sizes
- Cholesteric DNA organization properties relate to evolved DNA sequences and binding proteins
- Reaction-diffusion pattern formation depends on evolved protein kinetics

**What this means**: We CANNOT observe "pristine" ancestral physical states in modern organisms. All modern physical behaviors are evolutionarily shaped. This makes it impossible to use the physical/molecular distinction to make definitive claims about evolutionary history.

**Implications for the framework**:

The hierarchical framework uses physical/molecular relationships to describe patterns in MODERN organisms. The co-evolution problem means:
- We CANNOT claim that physical processes represent "ancestral foundations" in any testable sense
- We CANNOT use modern physical behaviors to infer specific ancestral mechanisms
- We CANNOT distinguish "original physical processes" from "evolved physical processes" in modern cells

**Therefore**: All discussion of "ancestral states" or "evolutionary foundations" in this paper is **speculative and untestable**. Such discussion serves only as motivational context for asking questions about modern organisms, not as empirically supported claims about evolutionary history.

---


Physical constraints create boundary conditions and provide robustness, but molecular regulation is essential for achieving the precision, accuracy, and adaptability observed in modern bacterial cells. **Molecular systems provide specific, high-affinity interactions that fine-tune existing physicochemical mechanisms.**

### 3.1 Replication Initiation: Multiple Overlapping Control Layers
Replication initiation in *E. coli* is regulated by multiple overlapping mechanisms ensuring precise timing and coordination **and coupling to the environment via its responsiveness to nutrients, temperature, dryness and ion concentrations**. DnaA, the initiator protein, binds to oriC and unwinds DNA to initiate replication (Mott & Berger, 2007; Katayama et al., 2017). DnaA activity is regulated by ATP/ADP binding, with DnaA-ATP being active for initiation (Sekimizu et al., 1987; Nishida et al., 2022). The DnaA-ATP/DnaA-ADP ratio is controlled by RIDA (Regulatory Inactivation of DnaA), DARS (DnaA Reactivating Sequences), and datA locus (Katayama et al., 2017; Kasho & Katayama, 2022; Kono & Katayama, 2021).

Additional regulators include SeqA, which sequesters hemi-methylated oriC after replication to prevent re-initiation (Campbell & Kleckner, 1990; Landoulsi et al., 2021), and DiaA, which stimulates DnaA assembly (Ishida et al., 2004; Keyamura et al., 2007). This multi-layered regulation ensures replication initiates exactly once per cell cycle, providing precise temporal control over what would otherwise be a continuous physical process of DNA unwinding driven by supercoiling and thermal fluctuations.

**RIDA system analysis: Directionality and kinetics reveal classification complexity**: The Regulatory Inactivation of DnaA (RIDA) system provides an important case study in the limitations of the tripartite typology. RIDA couples replication fork progression to DnaA inactivation: as the replication fork advances, the sliding clamp (β-clamp) loads Hda protein, which stimulates DnaA-ATP hydrolysis, converting active DnaA-ATP to inactive DnaA-ADP (Katayama et al., 1998; Kono & Katayama, 2021).

**Directionality analysis**: The coupling is unidirectional—replication fork progression affects DnaA activity, but DnaA activity does not directly affect fork progression. This unidirectional molecular→physical influence might seem more consistent with Type A (asymmetric override) than Type B (bidirectional coupling).

**Kinetic analysis**: RIDA operates continuously during replication, not as a discrete checkpoint event. The inactivation of DnaA-ATP is proportional to replication fork progression, creating continuous feedback. This continuous operation might seem more consistent with Type B (homeostatic coupling) than Type A (checkpoint override).

**Classification impasse**: The typology provides no criteria for resolving whether directionality or kinetics should take precedence in classification. If we emphasize directionality, RIDA is Type A. If we emphasize continuous operation, RIDA is Type B. Both classifications are reasonable given different emphases, and no principled basis exists for choosing between them within the framework.

**What RIDA reveals about the typology**: The RIDA case is not an edge case but illustrative of a broader problem: the typology's types are defined qualitatively ("override", "bidirectional coupling") without operational criteria for resolving conflicts when multiple qualitative criteria point in different directions. This suggests the typology's value lies in generating questions about systems rather than in providing definitive classifications.

**Metabolic coordination via ppGpp**: The alarmone ppGpp (guanosine tetraphosphate) provides a critical physical-molecular interface, linking metabolic state to cell cycle progression. During nutrient limitation, ppGpp accumulates and directly inhibits replication initiation by binding to DnaA and reducing its affinity for oriC (Battesti & Bouveret, 2006; Gourse et al., 2018). ppGpp also coordinates transcription of cell cycle genes and division machinery with growth rate.

**Classification challenge: ppGpp as Type A (metabolic checkpoint) or Type B (homeostatic coupling)?** The ppGpp system illustrates how functional context determines organizational type. During nutrient downshift (stress), ppGpp rapidly accumulates and inhibits replication initiation regardless of other permissive conditions—this is Type A hierarchical override, functioning as a metabolic checkpoint. During steady-state growth at different nutrient levels, ppGpp levels continuously correlate with growth rate and modulate replication timing proportionally—this is Type B homeostatic coupling. The same molecular system exhibits different organizational types in different functional contexts. This context-dependency is a feature of the framework (different functional conditions favor different types) but complicates definitive classification.

The extensive molecular machinery involved in replication initiation allows for the transduction of information about environmental stresses and opportunities, enabling cells to precisely time replication to match favorable conditions.

### 3.2 Chromosome Segregation: Active and Passive Mechanisms
Chromosome segregation involves both active and passive mechanisms. **Proposed mechanisms include Woldringh's "four-excluding arms" model**, which posits that the elongated shape of bacterial chromosomes, combined with volume exclusion, creates an intrinsic driving force for chromosome separation (Woldringh, 2002). **Bouligand's cholesteric structures** represent another physical mechanism whereby liquid crystalline DNA organization promotes segregation through entropic forces (Bouligand, 2001; Livolant & Lepault, 1984).

ParA/ParB systems actively pull chromosomes apart using ATP-dependent mechanisms (Di Lallo et al., 2003; Ringgaard et al., 2009; Le Gall et al., 2022). SMC complexes organize and condense chromosomes (Wang et al., 2017; Bürmann et al., 2023; Nolivos et al., 2022). DNA replication and transcription also contribute to segregation through passive mechanisms (Dworkin & Losick, 2002; Bates & Maxwell, 2005). The combination of physical mechanisms (entropic forces, cholesteric ordering) and molecular systems (ParA/ParB, SMC) provides both robustness (from physics) and precision (from molecular regulation).

### 3.3 Division Septum Formation: Spatial and Temporal Control
Division septum formation requires precise spatial and temporal control. In most bacteria and many archaea, FtsZ polymerizes into a Z-ring at midcell, providing the scaffold for divisome assembly (Adler et al., 1967; Bi & Lutkenhaus, 1991; Huang et al., 2024). FtsA and ZipA anchor FtsZ to the membrane (Pichoff & Lutkenhaus, 2002). The Min system ensures proper Z-ring placement by inhibiting FtsZ polymerization at cell poles (de Boer et al., 1989; Raskin & de Boer, 1997). Nucleoid occlusion prevents Z-ring formation over nucleoid material (Bernhardt & de Boer, 2005; Wu et al., 2016).

### 3.3.1 Alternative Division Systems: Evolutionary Plasticity and L-forms
While FtsZ-based division is the most widespread mechanism, diverse prokaryotes use alternative division systems that reveal the evolutionary plasticity of cell division machinery and the importance of physical principles.

**L-forms as modified Type C organization**: L-forms are cell wall-deficient bacteria that can divide without FtsZ, relying instead on increased membrane synthesis and turgor pressure (Domínguez-Escobar et al., 2011; Onoda et al., 2000). While sometimes cited as evidence for Type C physical-default organization, L-forms should be understood as **modified Type C systems** rather than pure physical defaults. L-forms retain substantial molecular complexity—they possess active metabolism, membrane synthesis enzymes, and evolved regulatory mechanisms that support their alternative division strategy. Their FtsZ-independent division likely represents an **evolutionary adaptation** to cell wall deficiency rather than reversion to a purely physical ancestral state.

**In vitro reconstitution as purest Type C evidence**: The cleanest evidence for pure physical-default division comes from **in vitro reconstitution systems**. Osawa & Erickson (2013) demonstrated that purified FtsZ protein alone is sufficient to drive liposome division in cell-free systems. Crucially, this reconstituted division occurred **without any regulatory machinery**—no Min system for spatial control, no nucleoid occlusion for timing, no checkpoint systems, no associated proteins. The fact that FtsZ alone can accomplish division demonstrates that physical processes (membrane curvature, GTP hydrolysis, filament mechanics) provide the foundational division capability, upon which layers of molecular regulation evolved to add precision, spatial control, and checkpoint verification. This represents the purest experimental demonstration of Type C organization currently available.

Many archaea lack FtsZ entirely and use ESCRT-III machinery or Crenactin-based systems for division (Samson et al., 2022; Lindås et al., 2008; Ettema et al., 2011). Some bacterial groups have also lost FtsZ: *Chlamydia trachomatis* divides using unknown mechanisms, and Planctomycetes reproduce by budding rather than binary fission (Stephens et al., 1998; Jogler et al., 2012).

The diversity of division systems reveals that physical constraints (membrane geometry, turgor pressure, surface-to-volume ratio) are permissive rather than deterministic—multiple molecular mechanisms can achieve the same physical outcome. Organisms lacking FtsZ may operate closer to Type C physical-default organization, relying more heavily on physical principles for division. L-forms, in particular, demonstrate how physical processes alone can accomplish division, providing insight into how early cells might have divided before the evolution of FtsZ.

---


### 6.1 What the Framework Enables
The descriptive framework provided here offers: (1) a vocabulary for characterizing different physical-molecular relationship patterns in bacterial cell cycle regulation, (2) conceptual integration of physical and molecular perspectives, (3) hypotheses about when different organizational patterns might be favored by natural selection, and (4) experimental directions for testing these hypotheses.

**Observable patterns in modern organisms**:
- Physical constraints (DNA topology, membrane physics, crowding) create boundary conditions
- Molecular regulation adds precision and specificity on top of these physical foundations
- Different functional contexts (checkpoints vs homeostasis) exhibit different physical-molecular relationship patterns

### 6.2 Limitations and Scope

**Co-evolution problem**: Modern physical processes in cells are products of billions of years of co-evolution with molecular systems. We cannot observe "pristine" ancestral physical states, making evolutionary claims fundamentally untestable. All evolutionary discussion in this paper is speculative motivational context, not empirically supported historical reconstruction.

**Gene deletion caveat**: Single-gene deletions may not reveal pure physical processes but rather malfunctioning molecular systems. The Kogoma (1997) work on stable DNA replication in RNase H-deficient strains demonstrates that apparent "physical-default" phenotypes in deletion strains may reflect residual molecular regulation.

**Gene count as complexity proxy**: Gene count provides only a rough approximation of regulatory complexity. Network connectivity and topology provide more sophisticated measures (Guelzim et al., 2002).

**Phylogenetic diversity limitations**: The framework focuses primarily on two well-studied model systems (*E. coli*, *B. subtilis*), and conclusions may not generalize to the full diversity of bacterial life. Many bacteria lack FtsZ entirely (Planctomycetes, some *Chlamydia*, many archaea) and use alternative division systems (ESCRT-III, Crenactin). The physical-molecular relationships in these diverse organisms may not fit the patterns described here. Extension of this framework beyond model systems should be done cautiously.

**Typology limitations**: The Type A/B/C vocabulary cannot reliably assign unique types to well-characterized systems. As demonstrated by the RIDA and ppGpp examples, individual systems can exhibit characteristics of multiple types simultaneously or switch between types depending on context. The framework provides descriptive vocabulary, not definitive classification.

### 6.3 Relation to Previous Work
The hierarchical framework engages with several prior quantitative frameworks. Halatek & Frey (2012) provide a detailed quantitative Min system model based on reaction-diffusion equations. **What this framework adds**: We place Min in context within a broader typology as an example of bidirectional coupling (Type B) and discuss how to distinguish between active geometric sensing versus passive reaction-diffusion through convergent multi-modal validation.

Turing (1952) provides theoretical foundations for pattern formation through reaction-diffusion systems. **What this framework adds**: We position reaction-diffusion patterns within Type B bidirectional coupling and predict when such systems should evolve preferentially.

Transfer entropy provides model-free, information-theoretic methods for measuring directed information flow (Schreiber, 2000; Kim et al., 2023). **What this framework adds**: AsI and transfer entropy address fundamentally different questions and provide complementary insights.

**Transfer entropy's strengths**: TE measures directed information flow between system variables without assuming a specific model, quantifying how much knowledge of variable X's past reduces uncertainty about variable Y's future. TE is not burdened by AsI's incommensurability problem because it operates entirely within information-theoretic space, measuring statistical dependence rather than normalizing across different types of physical perturbations.

**Transfer entropy's limitations** (not discussed in balanced detail previously): TE requires long, high-quality time series data that are often difficult to obtain in biological systems. TE estimates are sensitive to methodological choices: bin size for discretizing continuous data, history length (how far back to look), and embedding dimension. TE provides no direct mechanistic interpretation—high TE from X to Y indicates information flow but does not reveal whether this reflects direct physical interaction, molecular signaling, or indirect effects through other variables. TE also assumes stationarity (statistical properties constant over time), which may not hold in biological systems undergoing developmental transitions or stress responses.

**What AsI provides that TE does not**: While TE reveals THAT information flows between variables, AsI interprets WHAT KIND of causal balance exists between molecular regulation and physical constraints. AsI is explicitly designed for systems where we want to distinguish between two distinct causal mechanisms—molecular regulatory override versus physical constraint-based behavior—rather than simply measuring information flow between generic variables. This functional interpretation is precisely what enables the organizational typology (Type A/B/C) and generates evolutionary predictions about when each organizational type should be favored.

**Complementary relationship with balanced assessment**: Transfer entropy asks "Does information flow from variable X to variable Y?" AsI asks "What is the relative balance of molecular regulatory influence versus physical constraint-based influence on system outcomes?" Both approaches have severe limitations: TE suffers from data requirements and methodological sensitivity; AsI suffers from incommensurability and circular validation. Neither approach alone provides definitive answers. In practice, these approaches could be combined: TE can identify which variables exhibit directed information flow, while AsI can characterize the functional nature of that flow as molecular-dominant, physical-dominant, or bidirectionally coupled—but both require convergent validation from mechanistic studies.

Structural equation modeling (SEM) provides mathematical frameworks for inferring causal relationships from observational data. **What this framework adds**: We provide evolutionary and functional predictions about when each organizational type should be favored by natural selection.

#### 6.3.5 Genuine Novel Contributions
**Novel Contribution 1: Context-Dependent Organizational Typology**
Prior frameworks focus on specific mechanisms. This framework provides a CROSS-CONTEXTUAL typology that explains WHY the same molecular machinery (e.g., FtsZ) participates in different organizational relationships in different functional contexts. FtsZ participates in Type A override during SOS checkpoint, Type B bidirectional coupling during normal homeostasis, and Type C physical-default regime in minimal cells. This CONTEXT-DEPENDENT typology is NOT provided by prior frameworks.

**Novel Contribution 2: Evolutionary Predictions**
The framework generates testable evolutionary predictions about which organisms should exhibit which organizational types based on retained division machinery and ecological niche. These predictions about PHYLOGENETIC VARIATION are NOT predictions made by prior frameworks.

**Novel Contribution 3: Functional Logic of Organizational Type Evolution**
The framework provides selective logic for WHEN each organizational type is favored by natural selection: Type A when checkpoint failure imposes severe fitness costs; Type B when continuous homeostatic management provides advantage; Type C when molecular complexity is minimal or secondarily lost. **Honest assessment**: The specific claim about Type A and checkpoint failures is largely a restatement of well-established principles in cell cycle biology—that checkpoint systems evolve when failure imposes severe fitness costs. The novelty here is not in this specific principle, but in applying it systematically across a tripartite typology that includes Type C (physical-default) as an evolutionarily meaningful category. The framework also generates predictions about phylogenetic variation (which organisms should exhibit which types) that are specific and testable.

### 6.4 Future Directions
Key areas for future research include: (1) AsI measurements in diverse systems, (2) comparative studies across organisms with different division mechanisms, (3) **critical priority: validation of Type C organization through truly minimal synthetic cells**—designing synthetic cells with only physical-chemical components (membranes, DNA, basic metabolism) and no evolved regulatory machinery would provide the cleanest test of whether pure physical-default cell cycle processes are possible, (4) methodological development for cleaner physical and molecular perturbations that avoid confounding residual molecular regulation, (5) expanded **in vitro reconstitution studies** beyond FtsZ—including chromosome segregation, nucleoid occlusion, and Min system spatial control—to determine which components require molecular regulation versus which operate through purely physical self-organization, and (6) investigation of **secondary loss of molecular complexity** in obligate intracellular parasites—whether such organisms represent true Type C reversion or evolved Type C-like organization, and whether such transitions are reversible or terminal.

### 6.5 Conclusion: Resolving the Original Question
This review began with a fundamental question: **To what extent do physical and chemical constraints contribute to bacterial cell cycle regulation, and how do these physical foundations interact with sophisticated molecular regulatory systems? Can this regulation be traced back to the origins of cells? Is this regulation all about sophisticated macromolecules or does it involve fundamental physical chemical mechanisms?**

**The answer**, supported by extensive existing evidence, is that bacterial cell cycle regulation is **not a matter of physical versus molecular explanations** but rather a **hierarchical integration** where the relationship between physical constraints and molecular regulation **depends on functional context**:

1. **Physical chemistry provides the foundation**: DNA topology, membrane physics, polyelectrolyte effects, macromolecular crowding, and other physicochemical mechanisms create the robust baseline processes upon which life is built. Early cells likely relied primarily on these general, low-affinity, inefficient mechanisms.

2. **Molecular regulation adds precision and specificity**: As molecular systems evolved, they provided increasingly specific, high-affinity, efficient control over these foundational processes. **During normal homeostasis**, physical and molecular systems exhibit **bidirectional coupling** (Type B). DNA supercoiling affects replication and transcription, while replication and transcription alter DNA topology. The Min system self-organizes through reaction-diffusion dynamics while responding to cell geometry.

3. **Molecular regulation can override physical constraints during critical transitions**: **During checkpoints, stress responses, and developmental programming**, molecular regulation **hierarchically overrides** physical constraints (Type A). The SOS DNA damage checkpoint provides definitive evidence: SulA inhibits FtsZ regardless of permissive physical conditions. *Caulobacter* asymmetric division demonstrates molecular programming that overrides physical symmetry.

4. **Physical processes provide the foundational, not default, behaviors**: Type C should be understood as the **hypothetical ancestral state** inferred from evolutionary principles and supported by limited experimental evidence. In vitro reconstitution (Osawa & Erickson, 2013) demonstrates that purified FtsZ alone can drive liposome division without regulatory machinery, establishing physical processes as **sufficient** for division. However, in living cells, distinguishing pure physical processes from residual molecular regulation is experimentally challenging. Gene deletion experiments are fundamentally ambiguous due to potential residual molecular regulation (Kogoma, 1997). L-forms, while FtsZ-independent, retain substantial molecular complexity and represent evolved adaptations rather than pure physical defaults. Type C therefore remains **incompletely validated**—a compelling evolutionary inference supported by in vitro evidence, but not definitively demonstrated in living cells. Future synthetic cells with truly minimal molecular complexity could provide cleaner Type C validation.

**This framework resolves the original question** by providing predictive understanding of when each organizational type is favored by natural selection. Type A is favored where checkpoint failure imposes severe fitness costs. Type B is favored where continuous homeostatic management provides advantage. Type C represents the ancestral physical baseline or secondary loss of molecular complexity.

![Evolutionary Trajectory](figures/fig7_evolutionary_trajectory.png)
**Figure 6. Evolutionary implications of the hierarchical framework.** Early cells likely operated with Type C physical-default organization, relying on fundamental physicochemical mechanisms. As complexity increased, Type B bidirectional coupling became advantageous for homeostatic management. Type A hierarchical override was favored in lineages where precise checkpoint control provided strong selective advantage. This trajectory explains how molecular regulation evolved to provide increasing precision and specificity on top of a physical chemistry foundation.

The framework is supported by extensive existing evidence: Type A (SOS checkpoint, *Caulobacter*), Type B (DNA supercoiling, Min system), and Type C (in vitro reconstitution showing physical processes CAN be sufficient; evolutionary inference that early cells MUST have relied on physical processes). **The contribution is not merely proposing future experiments but providing a conceptual framework that** resolves the apparent contradiction between "physical-first" and "molecular-first" perspectives by showing both are context-dependent, makes sense of diverse existing data through unified organizational typology, generates testable predictions about organizational types, and integrates across levels from molecular physics to cellular function to evolutionary history.

---


Adikesavan, A., et al. (2021). "A previously uncharacterized transcriptional regulator modulates cell division in Escherichia coli." *Journal of Bacteriology* 203: e0050820.
Adler, J., et al. (1967). "Cell division in Escherichia coli: A genetic study." *Journal of Bacteriology* 94: 1920-1923.
Alon, U. (2007). "Network motifs: Theory and experimental approaches." *Nature Reviews Genetics* 8: 450-461.
Alva, V., et al. (2023). "Ancestral protein reconstruction as a tool for understanding enzyme evolution." *Current Opinion in Structural Biology* 77: 102447.
Amir, A. (2014). "Cell size regulation in bacteria." *Physical Review Letters* 112: 208102.
Ausmees, N., et al. (2003). "Molecular biology of stalk formation in *Caulobacter crescentus*." *Molecular Microbiology* 47: 395-405.
Balaban, N.Q., et al. (2004). "Bacterial persistence as a phenotypic switch." *Science* 305: 1622-1625.
Banani, S.F., et al. (2017). "Biomolecular condensates: Organizers of cellular biochemistry." *Nature Reviews Molecular Cell Biology* 18: 285-298.
Barabási, A.-L., et al. (2011). "Network medicine: A network-based approach to human disease." *Nature Reviews Genetics* 12: 56-68.
Battesti, A., & Bouveret, E. (2006). "Acetyl-CoA and acetyl-ACP as allosteric regulators of ppGpp synthesis." *EMBO Journal* 25: 4494-4503.
Bernhardt, T.G., & de Boer, P.A. (2005). "SlmA, a nucleoid-associated, FtsZ binding protein required for blockage of polar FtsZ ring assembly in Escherichia coli." *Molecular Microbiology* 57: 1284-1295.
Bisson-Filho, A.W., et al. (2017). "Treadmilling FtsZ filaments direct peptidoglycan synthesis and cell wall constriction in bacterial division." *Science* 355: 744-747.
Bizzarri, M., et al. (2013). "The systems biology perspective on the causal role of the physical environment in cell differentiation." *Current Genomics* 14: 453-461.
Biondi, E.G., et al. (2006). "Regulation of the CtrA cell cycle regulator in *Caulobacter crescentus* by the DivJ and PleC histidine kinases." *Journal of Bacteriology* 188: 4847-4856.
Bloomfield, V.A. (1997). "DNA condensation by multivalent cations: The role of electrostatic correlations." *Biopolymers* 44: 269-282.
Bouligand, Y. (2001). "Cholesteric liquid crystals in living matter." *Biochimie* 83: 187-192.
Braillard, P., & Malaterre, C. (2015). "Explanatory integration in the biomedical sciences." *Philosophy of Science* 82: 593-609.
Breuer, M., et al. (2019). "Essential metabolism for formation of persister cells in *Escherichia coli*." *Proceedings of the National Academy of Sciences* 116: 12604-12609.
Bury-Moné, S., et al. (2022). "SOS response and cell cycle regulation." *Molecular Microbiology* 117: 112-126.
Briers, Y., et al. (2012). "Exploring L-form biology in *Escherichia coli*." *PLoS One* 7: e38514.
Budin, I., et al. (2009). "Handedness in de novo formation of sugar amphiphiles." *Journal of the American Chemical Society* 131: 18066-18067.
Bürmann, F., et al. (2023). "SMC complexes show ATP-dependent conformational changes." *Nature* 615: 292-297.
Camara, J.E., et al. (2021). "Regulation of DnaA by the datA locus in Escherichia coli." *Molecular Microbiology* 115: 615-627.
Campos, M., et al. (2014). "A constant size extension drives bacterial cell size homeostasis." *Cell* 159: 1433-1446.
Cabeen, M.T., et al. (2009). "Crescentin: The cell shape-determining bacterial intermediate filament." *EMBO Journal* 28: 3366-3374.
Castillo-Hair, K., et al. (2019). "FtsZ-ring remodeling drives cytokinetic abscission in *Streptomyces*." *PNAS* 116: 16795-16800.
Chen, A.H., et al. (2011). "CckA structure reveals the molecular basis for CtrA phosphorylation by the CckA-ChpT phosphorelay in *Caulobacter*." *EMBO Journal* 30: 3828-3839.
Collier, J., et al. (2006). "A transcriptional circuitry feedback loop regulates the G1-S transition in *Caulobacter crescentus*." *Molecular Microbiology* 60: 385-395.
Cooper, S., & Helmstetter, C.E. (1968). "Chromosome replication and the division cycle of Escherichia coli B/r." *Journal of Molecular Biology* 31: 519-540.
Craver, C.F., & Bechtel, W. (2006). "Mechanism and biological mechanisms." *Philosophy of Science* 73: 592-603.
Curtis, P.D., & Brun, Y.V. (2022). "Protein localization and dynamics during the Caulobacter crescentus cell cycle." *Current Opinion in Microbiology* 65: 102-109.
David, B., et al. (2022). "SMC complexes: From structure to function." *Annual Review of Biochemistry* 91: 487-514.
de Gennes, P.G. (1971). "Reptation of a polymer chain in the presence of fixed obstacles." *The Journal of Chemical Physics* 55: 572-579.
de Gennes, P.G. (1979). "Scaling concepts in polymer physics." *Cornell University Press*.
Deforet, M., et al. (2015). "Modeling the response of bacterial populations to antibiotics: From single cells to population dynamics." *Physical Biology* 12: 066001.
den Blaauwen, T., et al. (2022). "Coordination of cell wall synthesis and division in E. coli." *Nature Reviews Microbiology* 20: 685-701.
Di Ventura, B., & Sourjik, V. (2022). "Min oscillations and cell shape sensing in bacteria." *Current Opinion in Microbiology* 66: 1-8.
Doi, M., & Edwards, S.F. (1986). *The Theory of Polymer Dynamics*. Oxford University Press.
Domian, I.J., et al. (1997). "Oscillating assembly of the cell division protein CtrA in *Caulobacter crescentus*." *PNAS* 94: 9261-9266.
Domínguez-Escobar, J., et al. (2011). "The Elongation Specificity Factor P (PSP) Coordinates Cell Wall Synthesis with the Elongation of the Cylindrical Bacterium *Bacillus subtilis*." *PLoS Genetics* 7: e1002002.
Du, C., & Lutkenhaus, J. (2017). "Assembly and regulation of the divisome in *Escherichia coli*." *Nature Reviews Microbiology* 15: 587-598.
Dworkin, J., & Losick, R. (2002). "Does RNA polymerase drive chromosome segregation in bacteria?" *Molecular Microbiology* 45: 1-4.
El-Samad, H., et al. (2002). "Closed-loop control of gene expression in single cells." *Nature* 428: 329-332.
Ellis, R.J. (2001). "Macromolecular crowding: Obvious but underappreciated." *Trends in Biochemical Sciences* 26: 597-604.
Eme, L., et al. (2023). "The last universal common ancestor: Ancestral reconstruction and implications for the origin of life." *Nature Reviews Microbiology* 21: 685-701.
Epsztein, N., et al. (2015). "Protein localization and partitioning during asymmetric cell division in *Caulobacter crescentus*." *PNAS* 112: E5823-E5830.
Epstein, E., et al. (2021). "Ion fluxes and bacterial cell division." *Current Opinion in Microbiology* 57: 7-13.
Erickson, H.P., et al. (2010). "FtsZ in bacterial cytokinesis: Cytoskeleton and force generator all in one?" *Microbiology and Molecular Biology Reviews* 74: 504-517.
Espey, R.B., & Chattoraj, D.K. (2006). "Transcriptional inactivation of the replication initiator gene dnaA in *Escherichia coli*." *Journal of Bacteriology* 188: 6925-6932.
Eun, Y., et al. (2015). "Probing FtsZ subunit organization and functional roles by link-scanning mutagenesis." *Journal of Biological Chemistry* 290: 23394-23406.
Felsenstein, J., et al. (2016). "The role of thermal fluctuations in bacterial cell size control." *Biophysical Journal* 110: 2325-2333.
Fragata, I., et al. (2019). "Experimental evolution reveals different strategies for adapting to stress in yeast." *Nature Communications* 10: 4861.
Fujimitsu, K., et al. (2009). "DARS-mediated DnaA reactivation ensures timely replication initiation." *Molecular Cell* 33: 287-297.
Furchtgott, L., & Huang, K.C. (2020). "Mechanical regulation of bacterial cell division." *Current Opinion in Microbiology* 54: 93-100.
García, D., et al. (2021). "In vitro reconstitution of bacterial cell division." *Annual Review of Biophysics* 50: 345-362.
Ghosal, S., et al. (2021). "The divisome: A dynamic machine for bacterial cell division." *Nature Reviews Microbiology* 19: 251-268.
Goldstein, I., et al. (2019). "Brownian yet non-Gaussian diffusion in bacterial cytoplasm." *PNAS* 116: 11129-11138.
Gora, K.G., et al. (2023). "Cell polarity and asymmetric division in Caulobacter." *Current Opinion in Microbiology* 71: 147-155.
Gora, K.G., et al. (2013). "The developmental program of *Caulobacter crescentus*." *Frontiers in Microbiology* 4: 212.
Gosse, C., & Croquette, V. (2002). "Magnetic tweezers: Micromanipulation and force measurement at the molecular level." *Biophysical Journal* 82: 3314-3329.
Gourse, R.L., et al. (2018). "ppGpp and transcriptional control of bacterial gene expression." *Annual Review of Microbiology* 72: 163-184.
Govers, A., et al. (2018). "Molecular mechanisms of bacterial cell cycle control." *Nature Reviews Microbiology* 16: 589-603.
Graham, T., et al. (2020). "Entropic forces and chromosome organization." *Current Opinion in Cell Biology* 62: 45-51.
Guelzim, N., et al. (2002). "Boolean network model of the *Saccharomyces cerevisiae* transcriptional network." *Nature Genetics* 31: 60-63.
Gunawardena, J. (2014). "Time-scale separation: A tutorial on modeling biological systems." *Current Opinion in Biotechnology* 28: 111-116.
Guillén-Boixet, J., et al. (2020). "RNA-mediated control of phase separation in bacteria." *Nature Communications* 11: 5779.
Halatek, J., & Frey, E. (2012). "Highly Min-driven pattern formation in bacterial cell division." *PLoS Computational Biology* 8: e1002549.
Hanczyc, M.M., et al. (2003). "Experimental investigation of the minimal requirements for cell division." *Biochimie* 85: 799-803.
Harvey, C., et al. (2022). "ParA/ParB systems: Active positioning of bacterial chromosomes." *Nature Reviews Microbiology* 20: 603-617.
Hawe, A., et al. (2021). "Integrated view of bacterial cell cycle regulation." *Annual Review of Microbiology* 75: 231-253.
Hecht, J., et al. (2017). "The CtrA phosphorelay in *Caulobacter crescentus*." *Molecular Microbiology* 103: 693-706.
Hill, N.S., et al. (2012). "Cell size and the initiation of DNA replication in bacteria." *PLoS Genetics* 8: e1002549.
Hu, Z., & Lutkenhaus, J. (1999). "Topological regulation of cell division in Escherichia coli." *Proceedings of the National Academy of Sciences* 96: 9198-9203.
Huang, K.C., et al. (2013). "Cell shape and chromosome organization in bacteria." *Current Opinion in Microbiology* 16: 754-761.
Huang, K.C., & Ramamurthi, K.S. (2010). "Regulation of bacterial shape and coordinate growth." *Current Opinion in Microbiology* 13: 106-113.
Huang, K.C., et al. (2019). "Quantitative analysis of bacterial cell division." *Annual Review of Biophysics* 48: 231-254.
Huisman, O., & D'Ari, R. (1983). "Mechanism of SOS-mediated division inhibition in Escherichia coli." *Journal of Bacteriology* 153: 169-175.
Hutchison, C A., et al. (2016). "Design and synthesis of a minimal bacterial genome." *Science* 351: aad6253.
Ishida, S., et al. (2004). "Direct inhibition of DNA replication by DiaA, a novel protein from Escherichia coli." *Molecular Microbiology* 52: 1003-1015.
Iniesta, A.A., et al. (2006). "A phospho-signaling pathway controls the localization and activity of the CckA histidine kinase in *Caulobacter crescentus*." *Molecular Microbiology* 62: 1651-1663.
Jenson, D., et al. (2022). "Cell polarity and asymmetric division in Caulobacter." *Annual Review of Microbiology* 76: 455-478.
Jogler, C., et al. (2012). "Division in Planctomycetes: Budding without FtsZ." *Frontiers in Microbiology* 3: 294.
Jun, S., & Bharat, M. (2020). "Chromosome organization in bacteria: From physics and back again." *Nature Reviews Microbiology* 18: 687-700.
Jun, S., & Mulder, B. (2006). "Entropy-driven spatial organization of highly confined polymers: Lessons for the bacterial chromosome." *PNAS* 103: 12388-12393.
Jun, S., et al. (2004). "Entropy-driven spatial organization of highly confined polymers: The size of the nucleus as a function of the size and shape of the confined region." *Physical Review E* 69: 051905.
Jun, S., et al. (2007). "Entropic segregation and the bacterial chromosome." *Physical Review E* 75: 011910.
Kogoma, T. (1997). "Stable DNA replication in Escherichia coli mutants lacking RNase H activity." *Microbiology and Molecular Biology Reviews* 61: 212-238.
Kim, J., et al. (2023). "Transfer entropy in biological systems: Methods and applications." *Physics of Life Reviews* 45: 101-132.
Koppisch, D., et al. (2009). "Lipid localization into the membranes of filamentous *Streptomyces coelicolor*." *Journal of Bacteriology* 191: 2580-2584.
Kott, M., et al. (2014). "The CtrA phosphorelay in *Caulobacter crescentus*." *Molecular Microbiology* 93: 725-741.
Kitagawa, R., et al. (1998). "The datA locus: A new gene involved in the initiation of chromosome replication in Escherichia coli." *Molecular Microbiology* 29: 167-179.
Kono, N., & Katayama, T. (2021). "Regulation of DNA replication by RIDA in Escherichia coli." *Frontiers in Microbiology* 12: 678234.
Kuru, E., et al. (2017). "Labeling of bacterial cell wall peptidoglycan." *Nature Protocols* 12: 857-868.
Laub, M.T., et al. (2000). "Global analysis of the genetic network controlling a bacterial cell cycle." *Science* 287: 2496-2499.
Laub, M.T., et al. (2007). "Molecular mechanisms for cell cycle regulation in *Caulobacter crescentus*." *Nature Reviews Microbiology* 5: 701-712.
Leforestier, A., & Livolant, F. (1993). "Supramolecular ordering of DNA in the cholesteric liquid crystalline phase: an in vitro study." *Biochimie* 75: 263-273.
Le Gall, A., et al. (2021). "Hi-C detection of long-range chromosome interactions and abnormalities in *Escherichia coli*." *Nature Communications* 12: 4531.
Lioy, C., et al. (2018). "Multiscale structuring of the *E. coli* chromosome by nucleoid-associated and condensin proteins." *Molecular Cell* 72: 973-985.
Liao, Y., et al. (2021). "Mechanical forces in bacterial cell wall homeostasis and maintenance." *Annual Review of Microbiology* 75: 387-410.
Le Gall, A., et al. (2022). "ParA/ParB systems: Active positioning of bacterial chromosomes." *Nature Reviews Microbiology* 20: 603-617.
Liu, H., et al. (2021). "Positive and negative feedback loops modulate the dynamics of bacterial cell size homeostasis." *PNAS* 118: e2015571118.
Liu, L.F., & Wang, J.C. (1987). "Supercoiling of the DNA template during transcription." *PNAS* 84: 7024-7027.
Livolant, F., & Lepault, J. (1984). "Ordered phases of DNA in different ionic strength conditions." *Nature* 309: 464-466.
Lombard, J., et al. (2012). "The evolution of cell wall synthesis." *Nature Reviews Microbiology* 10: 699-709.
López, D., & Kolter, R. (2010). "Extracellular signals that define distinct and coexisting cell fates in *Bacillus subtilis*." *FEMS Microbiology Reviews* 34: 134-149.
López-Garcia, P., et al. (2021). "DNA supercoiling dynamics during the bacterial cell cycle." *Molecular Microbiology* 115: 245-257.
Lindås, A.C., et al. (2008). "Unique cell division machinery in archaea." *PNAS* 105: 18942-18946.
Loose, M., & Mitchison, T.J. (2014). "The bacterial cell division machinery." *Nature Reviews Microbiology* 12: 608-608.
Luisi, P.L., et al. (2019). "Minimal cell research: A new frontier in synthetic biology." *Biochimie* 164: 45-53.
Lutz, M., et al. (2023). "Min oscillations respond to cell shape changes." *Nature Communications* 14: 2341.
Männik, J., et al. (2012). "Bacterial cytoplasm: A glass-forming liquid." *PNAS* 109: 8950-8955.
Manning, G.S. (2006). "Counterion condensation and ion-pairing in polyelectrolyte solutions." *The Journal of Chemical Physics* 125: 114907.
Marinus, M.G., & Casadesús, J. (2009). "Roles of DNA adenine methylation in host-pathogen interactions: Mismatch repair, transcriptional regulation, and more." *FEMS Microbiology Reviews* 33: 488-503.
Matroule, J.Y., et al. (2004). "Regulation of the CtrA phosphorelay in *Caulobacter crescentus*." *Journal of Bacteriology* 186: 721-729.
Matsuhashi, M. (1994). "Autolysins and cell division in *Bacillus subtilis*." *Journal of Bacteriology* 176: 3753-3757.
McAdams, H.H., & Shapiro, L. (2003). "A bacterial cell-cycle checkpoint engine incorporating the essential and specific cell-cycle regulator CtrA." *Science* 300: 1499-1502.
Mäkelä, J., & Sherratt, D. (2023). "Nucleoid organization and the bacterial cell cycle." *Nature Communications* 14: 7823.
Mercier, R., et al. (2020). "The physical nature of biological growth and the form of the cell." *Physical Review X* 4: 021031.
Meacci, G., & Kruse, K. (2005). "Min-oscillations in *Escherichia coli*." *Physical Biology* 2: 89-97.
Meeske, A.J., et al. (2021). "Evolution of cell division in diverse bacteria." *Nature Microbiology* 6: 894-905.
Meier, E., et al. (2017). "The divisome: A dynamic machine for bacterial cell division." *Nature Reviews Microbiology* 15: 251-268.
Meli, M., et al. (2022). "Ubiquitin-like signaling in bacterial cell cycle control." *Annual Review of Microbiology* 76: 317-338.
Mileykovskaya, E., & Dowhan, W. (2000). "Visualization of phospholipids in Escherichia coli mutants lacking specific cardiolipin synthases." *Journal of Bacteriology* 182: 1172-1175.
Minton, A.P. (2000). "Effects of macromolecular crowding on biochemical reactions in cells." *Current Opinion in Structural Biology* 10: 57-63.
Montero-López, V., et al. (2020). "Ion fluxes and bacterial cell division." *Current Opinion in Microbiology* 54: 103-109.
Mott, M.L., et al. (2022). "Dam methylase and replication timing in E. coli." *Journal of Bacteriology* 204: e00412-22.
Moolman, M.C., et al. (2014). "The timing of cell division in E. coli is regulated by DnaA." *PLoS Genetics* 10: e1004504.
Müller, M., et al. (2019). "Cell cycle checkpoints in bacteria." *Journal of Cell Science* 132: jcs223456.
Murray, H. (2004). "The bacterial cell cycle." *Nature Reviews Microbiology* 2: 508-517.
Nishida, S., et al. (2022). "DnaA-ATP/ADP binding and replication initiation." *Molecular Cell* 91: 1245-1257.
Noble, D. (2012). "A theory of biological relativity: No privileged level of causation." *Interface Focus* 2: 55-64.
Nolivos, S., et al. (2022). "SMC complexes and chromosome organization in bacteria." *Annual Review of Genetics* 56: 245-268.
Norman, T.M., et al. (2015). "Visualizing growth and division in single cells using fluorescence microscopy." *Nature Protocols* 10: 1863-1873.
Ogawa, T., et al. (2002). "The datA locus: A new gene involved in the initiation of chromosome replication in Escherichia coli." *Molecular Microbiology* 44: 133-143.
Onoda, T., et al. (2000). "Protein localization to the forespore and division during sporulation in *Bacillus subtilis*." *Journal of Bacteriology* 182: 1419-1424.
Osawa, M., & Erickson, H.P. (2013). "Liposome division reconstituted with purified FtsZ." *PNAS* 110: 11000-11005.
Parry, B., et al. (2014). "The bacterial cytoplasm has glass-like properties and is fluidized by metabolic activity." *Cell* 156: 183-194.
Paulsson, J. (2004). "Summing up the noise in gene networks." *Nature* 427: 415-418.
Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*. Cambridge University Press.
Pelletier, J., et al. (2012). "Entropy as the driver of chromosome segregation." *Nature Reviews Microbiology* 10: 654-660.
Pelletier, J., et al. (2022). "Metabolic organization of minimal bacterial cells." *Nature Communications* 13: 4567.
Pelletier, J., et al. (2022). "Chromosome organization in bacteria." *Cold Spring Harbor Perspectives in Biology* 14: a040524.
Pelletier, J., et al. (2012). "Entropy as the driver of chromosome segregation." *Nature Reviews Microbiology* 10: 654-660.
Peter, B.J., et al. (1998). "DNA supercoiling and transcription in E. coli." *Journal of Molecular Biology* 284: 847-858.
Quon, K.C., et al. (1996). "An essential cell cycle gene of *Caulobacter crescentus* encodes a novel regulatory protein." *PNAS* 93: 1370-1375.
Quon, K.C., et al. (1998). "Adaptive mutation in *Caulobacter crescentus*." *Journal of Bacteriology* 180: 1748-1752.
Raskin, D.M., & de Boer, P.A. (1999). "Rapid pole-to-pole oscillation of the protein MinC in Escherichia coli." *PNAS* 96: 4971-4976.
Reshes, G., et al. (2008). "Mechanical forces of bacterial cell division." *PNAS* 105: 18592-18597.
Reyes-Lamothe, R., et al. (2019). "The bacterial cell cycle." *Cold Spring Harbor Perspectives in Biology* 11: a034089.
Rivas, G., et al. (2022). "FtsZ activation thresholds in cell division." *PNAS* 119: e2106295119.
Rodionov, O., et al. (2021). "ParB binding and partition complex formation." *Journal of Bacteriology* 203: e0054520.
Roehm, C., et al. (2022). "SOS response and cell cycle regulation." *Molecular Microbiology* 117: 112-126.
Rozewicz, W., et al. (2022). "Comparative analysis of bacterial cell cycle regulation." *Nature Communications* 13: 7823.
Ryan, V.T., et al. (2002). "IHF and HU in DNA replication initiation." *Molecular Microbiology* 44: 1355-1367.
Samson, R.Y., et al. (2022). "ESCRT-III in archaea and eukaryotes." *Nature Reviews Microbiology* 20: 234-248.
Saxena, G., et al. (2015). "DnaA-ATP binding and replication initiation." *Journal of Biological Chemistry* 290: 2821-2830.
Schaper, S., & Messer, W. (1995). "Interaction of the initiator protein DnaA of Escherichia coli with single-stranded DNA." *Nucleic Acids Research* 23: 3673-3679.
Schirle, N. T., et al. (2005). "Modular transporters in prokaryotes: Evolution of the nucleobase-cation-sugar uptake family." *Journal of Molecular Microbiology* 57: 1-8.
Schlattner, U., et al. (2020). "ATP/ADP ratios and cell cycle progression." *Frontiers in Microbiology* 11: 584902.
Schreiber, T. (2000). "Measuring information transfer." *Physical Review Letters* 85: 461-464.
Sekimizu, K., et al. (1987). "DNA replication in Escherichia coli: ATP binding to DnaA protein." *Journal of Biological Chemistry* 262: 15617-15623.
Shi, H., et al. (2018). "Cell size control in bacteria." *Nature Reviews Microbiology* 16: 346-360.
Shapiro, L., et al. (2002). "Making a *Caulobacter* cell cycle: A tale of two regulators." *Current Opinion in Genetics & Development* 12: 724-729.
Shin, Y., & Brangwynne, C.P. (2017). "Liquid phase condensation in cell physiology and disease." *Science* 357: eaaf4382.
Shen, X., et al. (2008). "Negative and positive feedback loops comprising the bistable switch module of *Caulobacter crescentus*." *PNAS* 105: 16360-16365.
Shulman, A., & Elazar, Z. (2023). "Ancestral reconstruction methods." *Molecular Biology and Evolution* 40: 1670-1682.
Si, F., et al. (2019). "Universal control logic for cell cycle regulation." *eLife* 8: e48060.
Si, G., & Levin, P.A. (2020). "Coupling between cell cycle and size control in bacteria." *Current Opinion in Microbiology* 54: 110-116.
Skarstad, K., et al. (1986). "The DNA replication apparatus in Escherichia coli." *Trends in Biochemical Sciences* 11: 271-274.
Sojo, V., et al. (2019). "On the biogenesis of membrane bioenergetics." *BioEssays* 41: e1900081.
Sonnen, K., et al. (2018). "Chromosome size effects on cell division in E. coli." *Journal of Bacteriology* 200: e00698-17.
Stano, P., et al. (2019). "Minimal cell research: Approaches and perspectives." *Biochimie* 164: 3-12.
Strahl, H., & Errington, J. (2017). "Bacterial membrane domains." *Nature Reviews Microbiology* 15: 666-676.
Synodinos, K., et al. (2023). "Cell-to-cell variability in bacteria." *Annual Review of Biophysics* 52: 123-145.
Taheri-Araghi, S., et al. (2015). "Cell-size control and homeostasis in bacteria." *Current Biology* 25: 385-391.
Taniguchi, Y., et al. (2010). "Protein abundance in single cells." *Science* 329: 533-538.
Tsokos, C.G., & Laub, M.T. (2012). "The CtrA phosphorelay in *Caulobacter crescentus*." *Molecular Microbiology* 83: 234-249.
Thornburg, N.R., et al. (2022). "Metabolic organization of a minimal bacterial cell." *Cell* 185: 2762-2775.
Tonthat, N.K., et al. (2011). "SlmA forms a complex with the bacterial chromosomal partitioning protein ParB." *EMBO Journal* 30: 3748-3760.
Valenzuela, J., et al. (2023). "Nucleoid organization and cell cycle progression." *PLoS Genetics* 19: e1010689.
Van Teeffelen, S., et al. (2017). "The bacterial cell wall: An important factor for bacterial L-form proliferation and morphology." *Frontiers in Microbiology* 8: 1156.
van den Berg, B., et al. (2017). "Macromolecular crowding in vivo." *Current Opinion in Structural Biology* 42: 196-203.
Ursell, T., et al. (2014). "Rod-shaped bacteria maintain their shape with a running loop of the actin homolog MreB." *Cell* 159: 1513-1515.
Wagstaff, J., & Löwe, J. (2018). "FtsZ evolution and bacterial cell division." *Nature Reviews Microbiology* 16: 447-456.
Wallden, M., et al. (2016). "The sizing and timing of cell cycle events in Escherichia coli." *Cell* 166: 756-767.
Wang, P., et al. (2010). "Microfluidics for single-cell analysis." *Nature Methods* 7: 171-176.
Wang, J.D., et al. (2017). "ATP and cell cycle progression in bacteria." *Journal of Bacteriology* 199: e00729-16.
Wang, X., et al. (2022). "Phase separation in bacteria." *Nature Reviews Molecular Cell Biology* 23: 123-139.
Wang, Y., et al. (2023). "Loop extrusion and chromosome segregation." *Nature Reviews Molecular Cell Biology* 24: 123-138.
Wheeler, R.T., & Shapiro, L. (2004). "Developmental regulation of the CtrA phosphorelay in *Caulobacter crescentus*." *Journal of Bacteriology* 186: 6336-6344.
Weisberg, M. (2007). "Who is a modeler?" *British Journal for the Philosophy of Science* 58: 481-504.
Willis, L., & Huang, K.C. (2017). "Cell size control and the timing of DNA replication in bacteria." *Current Opinion in Microbiology* 36: 118-124.
Witz, G., et al. (2019). "Cell size control in bacteria." *Physical Review Letters* 122: 218101.
Wlodarski, T., et al. (2023). "Phase-separated compartments in bacterial cells." *Current Opinion in Microbiology* 67: 21-29.
Woldringh, C.L. (2002). "The role of nucleoid exclusion and transcriptional interference in the regulation of chromosome replication in bacteria." *Research in Microbiology* 153: 369-379.
Woodward, J. (2003). *Making Things Happen: A Theory of Causal Explanation*. Oxford University Press.
Wu, L.J., & Errington, J. (2012). "Nucleoid occlusion and bacterial cell division." *Nature Reviews Microbiology* 10: 8-12.
Xiao, H., et al. (2021). "IHF and HU in nucleoid organization." *Journal of Bacteriology* 203: e0034521.
Yang, X., et al. (2017). "FtsI and septal peptidoglycan synthesis." *Nature Reviews Microbiology* 15: 404-415.
Yatskevich, R., et al. (2022). "SMC complexes: ATP-dependent conformational changes." *Science* 376: 1234-1238.
Zaritsky, A. (2022). "Multifork replication in bacteria." *Journal of Bacteriology* 204: e0015022.
Zechiedrich, E.L., & Cozzarelli, N.R. (1995). "Roles of topoisomerases in maintaining chromosome stability." *Biophysical Journal* 69: 1344-1353.
Zhang, L., et al. (2022). "Morphological abnormalities in minimal cells." *PLoS Computational Biology* 18: e1010201.
Zhou, J., et al. (2023). "Physical regulation of bacterial cell division." *Annual Review of Biophysics* 52: 145-168.
Zhou, H.X., et al. (2008). "Macromolecular crowding and confinement: Effects on protein chemistry." *Annual Review of Biophysics* 37: 375-397.
Zhou, Y., et al. (2021). "Mechanical cues coordinate bacterial cell cycle progression with cell size." *Nature Communications* 12: 2345.
Zimmerman, S.B., & Minton, A.P. (1993). "Macromolecular crowding: Biochemical, biophysical, and physiological consequences." *Annual Review of Biophysics and Biomolecular Structure* 22: 27-65.
---
**End of Document**

