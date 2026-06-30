# Phase 2: Computational/Informatic Secondary Analysis
## Database-Driven Complexity Metrics and Matrix Occupancy Quantification

**Date**: 2026-04-29
**Purpose**: Execute database survey to create rigorous complexity metrics and quantify matrix cell occupancy

---

## Analysis Plan

### Part A: STRING Database Network Analysis

**Objective**: Extract cell-cycle associated protein interaction networks for each target organism to create independent, database-derived complexity metrics

**Target organisms**:
1. *Escherichia coli* (strain K-12 MG1655)
2. *Bacillus subtilis* (strain 168)
3. *Caulobacter crescentus* (strain NA1000 or CB15)
4. *Mycoplasma pneumoniae* (strain M129)

**Data extraction protocol**:

1. **Access STRING database** (https://string-db.org)
   - Use API or web interface
   - Target: Protein-protein interaction networks

2. **Identify cell-cycle associated proteins**:
   - *E. coli*: DnaA, DnaB, DnaC, DiaA, SeqA, Dam, Hda, MinC, MinD, MinE, SlmA, FtsZ, FtsA, ZipA, ZapA, SulA, ParA, ParB, SMC subunits
   - *B. subtilis*: DnaA, DnaB, DnaD, DnaI, YabA, MinC, MinD, DivIVA, MinJ, Noc, FtsZ, FtsA, EzrA, SepF, ParA, ParB, SMC subunits
   - *C. crescentus*: DnaA, DnaB, CtrA, CckA, ChpT, DivJ, PleC, DivK, FtsZ, FtsA, MipZ, ParA, ParB, SMC subunits
   - *M. pneumoniae*: DnaA, DnaN, FtsZ (minimal set)

3. **Extract network properties for each organism**:
   - Node degree distribution (average degree, max degree)
   - Clustering coefficient
   - Network diameter
   - Number of connected components
   - Betweenness centrality
   - Closeness centrality

4. **Quantify cell-cycle subnetwork specifically**:
   - Extract only interactions between cell-cycle proteins
   - Calculate subnetwork properties independently
   - This becomes the database-derived complexity metric

**Expected output**: Table with network properties for each organism

| Organism | Network Nodes | Network Edges | Avg Degree | Clustering Coefficient | Network Diameter | Cell-cycle Subnetwork Nodes | Cell-cycle Subnetwork Edges |
|----------|---------------|---------------|------------|----------------------|------------------|----------------------------|--------------------------|
| E. coli | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] |
| B. subtilis | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] |
| C. crescentus | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] |
| M. pneumoniae | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] | [DATA] |

**Database-derived complexity score formula**:
- STRING_CCS = (Cell-cycle nodes × 1) + (Cell-cycle edges × 2) + (Avg degree × 5) + (Clustering coefficient × 3)

This provides an independent complexity metric that cross-validates the manual complexity scores from Phase 1.

---

### Part B: RegulonDB and SubtiWiki Matrix Occupancy Quantification

**Objective**: Explicitly map every regulatory interaction onto the matrix to create quantitative occupancy scores

**B.1: RegulonDB Analysis (E. coli)**

**Data source**: RegulonDB v10.0 (https://regulondb.ccg.unam.mx)

**Cell-cycle genes to extract**:
- Replication initiation: dnaA, dnaB, dnaC, diaA, seqA, dam, hda, datA, DARS1, DARS2, DARS3
- Replication control: rida (hda-uidA), other regulators
- Segregation: parA, parB, smc, mukB, mukE, mukF
- Division: ftsZ, ftsA, ftsI, ftsK, ftsL, ftsN, ftsQ, ftsW, zapA, zapB, zapC, minC, minD, minE, slmA, sulA
- Checkpoint: lexA, recA, sulA, relA (ppGpp synthesis), spoT (ppGpp degradation)

**Data to extract for each interaction**:
1. Regulator gene → Target gene
2. Type of regulation (activation, repression, dual)
3. Evidence level (confirmed, predicted, weak)
4. Physiological condition (if condition-specific)
5. Temporal mode (constitutive, condition-specific, growth phase-specific)

**Mapping to matrix cells**:
For each interaction, classify:
- **Directionality**:
  - Molecular→Physical: Gene regulation → Physical process (e.g., sulA → ftsZ inhibition)
  - Bidirectional: Both directions (e.g., DNA supercoiling ↔ transcription/replication)
  - Physical→Molecular: Physical process → Gene regulation (e.g., mechanosensing → gene expression)
- **Temporal mode**:
  - Continuous Homeostatic: Constitutive or steady-state expression
  - Episodic/Checkpoint: Induced by specific conditions
  - Constitutive Default: Always-on physical processes

**Quantitative occupancy score**:
For each matrix cell, calculate:
- Occupancy_Score(cell) = Σ(interaction_i × evidence_weight_i)
- Where evidence_weight: Confirmed = 3.0, Predicted = 1.0, Weak = 0.5

**Expected output**: Quantified matrix occupancy table

| Matrix Cell | Interaction Count | Occupancy Score | Top Interactions | Evidence Distribution |
|-------------|------------------|-----------------|-----------------|----------------------|
| (1,1) Molecular→Physical/Continuous | [COUNT] | [SCORE] | [LIST] | [DISTRIBUTION] |
| (1,2) Molecular→Physical/Episodic | [COUNT] | [SCORE] | [LIST] | [DISTRIBUTION] |
| ... | ... | ... | ... | ... |

**B.2: SubtiWiki Analysis (B. subtilis)**

**Data source**: SubtiWiki (https://subtiwiki.uni-goettingen.de/)

**Process**: Same as RegulonDB analysis but for B. subtilis genes

**Cell-cycle genes**:
- Replication: dnaA, dnaB, dnaD, dnaI, dnaN, yabA
- Segregation: parA, parB, smc, scpA, scpB
- Division: ftsZ, ftsA, ftsL, ftsW, ezrA, sepF, zapA, zapB, zapC, minC, minD, minJ, divIVA, noc
- Checkpoint: lexA, recA, relA, spoT

**Extract same data** as RegulonDB analysis

---

### Part C: Formal Test of "Forbidden Cells"

**Objective**: Determine whether cells (1,3) and (2,3) are truly empty or whether candidate systems exist

**Methodology**:
1. **Systematic search** through RegulonDB and SubtiWiki for:
   - Constitutively expressed genes that affect physical processes continuously
   - Candidates for Molecular→Physical/Constitutive Default or Bidirectional/Constitutive Default

2. **Candidate evaluation criteria**:
   - Is the system truly constitutive (expressed in all conditions)?
   - Is it physically "default" (operates without active regulation)?
   - Does it bridge molecular and physical domains?

3. **Expected findings**:
   - Most "constitutive" systems actually require active regulation (→ should be classified as Continuous Homeostatic, not Constitutive Default)
   - True "default" physical processes are rare in living organisms
   - This will provide rigorous justification for "unoccupied" status rather than "forbidden"

**Output**: Documented search methodology with explicit count of candidates considered and rejected, with rationale

---

## Implementation Timeline

**Week 1**: STRING database extraction and network analysis
**Week 2**: RegulonDB extraction and matrix mapping
**Week 3**: SubtiWiki extraction and matrix mapping
**Week 4**: Quantitative analysis, synthesis, and integration with D1 results

---

## Expected Contributions

**Novel informatic contribution**: No prior paper has systematically mapped all regulatory interactions from RegulonDB/SubtiWiki onto a physical-molecular framework. This creates a quantitative, database-driven analysis that complements the manual complexity scoring.

**Cross-validation**: Database-derived complexity scores can be compared to manual complexity scores to assess reliability and identify discrepancies.

**Rigorous forbidden cell test**: Explicit documentation of search methodology provides rigorous justification for "unoccupied" status rather than assertion of "forbidden" status.

**Publication value**: This transforms the current qualitative matrix occupancy table into a quantitative analysis with explicit sourcing and reproducible methodology.

---

## Data Management

**Data sources**: All database queries and extractions will be documented with:
- Database version and access date
- Query parameters used
- Gene lists extracted
- Interaction counts and types

**Reproducibility**:
- Scripts and query logs will be made available
- All extracted data will be archived in supplementary tables
- Methodology will be sufficiently detailed for independent replication

---

## Integration with Main Paper

**Where to include**:
- **Results Section 3.4**: Present quantitative matrix occupancy results
- **Methods Section 2.2**: Describe database extraction methodology
- **Supplementary Tables**: Full interaction lists and matrix mappings

**How it strengthens the paper**:
1. Provides second pillar of empirical contribution (alongside D1 correlation)
2. Creates database-driven complexity metrics that validate manual scoring
3. Rigorously tests "forbidden cell" hypothesis
4. Makes matrix occupancy survey quantitative rather than qualitative

**Visualization**: Network diagrams showing cell-cycle subnetworks for each organism, with nodes color-coded by matrix cell assignment
