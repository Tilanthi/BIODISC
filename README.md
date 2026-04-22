# BIODISC: Biology Discovery and Intelligence System

BIODISC is a unified AGI-inspired framework for autonomous hypothesis generation and validation in biology. The system integrates ~320,000 lines of clean, functional code across modular cognitive capabilities.

## Overview

BIODISC combines advanced AI techniques including:

- **Causal Inference & Discovery**: Structural causal models, PC algorithm, counterfactual reasoning, temporal causal discovery
- **Meta-Learning**: MAML optimization, cross-domain transfer learning, meta-discovery patterns
- **Swarm Intelligence**: Multi-agent reasoning, stigmergic coordination
- **Domain Expertise**: 10 specialized biology domain modules
- **Theory Engine**: Advanced theoretical reasoning and hypothesis generation
- **Meta-Cognitive Systems**: Multi-layered context representation, self-improvement, abstraction navigation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Tilanthi/BIODISC.git
cd BIODISC

# Install dependencies
pip install -e .
```

### Basic Usage

```python
from biodisc_core import create_biodisc_system

# Create system with auto-optimized capabilities
system = create_biodisc_system()

# Answer queries with automatic capability selection
result = system.answer("What causes protein misfolding?")
print(result['answer'])
```

### Discovery System

```python
from biodisc_core.discovery_orchestrator import create_discovery_orchestrator

# Create discovery system
orchestrator = create_discovery_orchestrator()

# Run autonomous discovery pipeline
results = orchestrator.discover(
    query="Investigate correlations between gene expression and disease phenotypes",
    data=your_data,
    capabilities=["temporal", "counterfactual", "triangulation"]
)
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Entry Points                                 │
│  create_biodisc_system() | process_query()                        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Theory Engine                                │
│  Theoretical reasoning | Hypothesis generation | Validation    │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│              Meta-Cognitive Capabilities                        │
│  Meta-Context Engine | Self-Compiler | Abstraction Navigator  │
│  Multi-Mind Orchestration                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Domain Architecture                          │
│  BaseDomainModule → DomainRegistry → Specialized Domains        │
│  (10 domains: Molecular Biology, Biochemistry, Genetics,        │
│   Cell Biology, Biophysics, Bioinformatics, Computational       │
│   Biology, Genomics, Proteomics, Systems Biology)               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                Cross-Domain Meta-Learning                       │
│  MAMLOptimizer | CrossDomainMetaLearner | AdaptationResult      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   Physics & Causal Engines                      │
│  UnifiedPhysicsEngine | StructuralCausalModel | PCAlgorithm      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  Memory & Knowledge Systems                     │
│  MORK Ontology | Memory Graph | Vector Store | Working Memory   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### Biology Domain Modules

Specialized domains covering:
- **Molecular Biology**: DNA replication, transcription, translation, gene expression
- **Biochemistry**: Metabolic pathways, enzyme kinetics, molecular interactions
- **Genetics**: Heredity, variation, mutations, genetic mapping
- **Cell Biology**: Cell structure, organelles, cell division, signaling
- **Biophysics**: Physical principles in biological systems
- **Bioinformatics**: Sequence analysis, structural biology
- **Computational Biology**: Biological modeling and simulation
- **Genomics**: Genome analysis, sequencing technologies
- **Proteomics**: Protein structure and function
- **Systems Biology**: Integrated biological networks

### Causal Reasoning

- **Structural Causal Models**: Represent and reason about causal relationships
- **PC Algorithm**: Discover causal structure from observational data
- **Counterfactual Reasoning**: Reason about what might have been
- **Temporal Causal Discovery**: Discover causal relationships over time
- **Biological Causal Discovery**: Specialized algorithms for biological systems

### Meta-Learning

- **MAML Optimization**: Fast adaptation to new biological tasks
- **Cross-Domain Transfer**: Apply knowledge across biological domains
- **Meta-Discovery Patterns**: Learn patterns of biological discovery

### Swarm Intelligence

- **Multi-Agent Reasoning**: Collaborative problem-solving
- **Stigmergic Coordination**: Indirect coordination through environment
- **Collective Intelligence**: Emergent problem-solving capabilities

### Theory Engine

- **Theoretical Reasoning**: Advanced logic and inference
- **Hypothesis Generation**: Automatic hypothesis creation
- **Validation Framework**: Systematic hypothesis testing

### Meta-Cognitive Systems

- **Meta-Context Engine (MCE)**: Dynamic context layering
- **Autocatalytic Self-Compiler (ASC)**: Recursive self-improvement
- **Cognitive-Relativity Navigator (CRN)**: Multi-scale abstraction reasoning
- **Multi-Mind Orchestration (MMOL)**: Specialized sub-minds

## Testing

```bash
# Run all tests
python biodisc_core/tests/test_specialist_capabilities.py

# Run V4 capability tests
python biodisc_core/tests/v4/run_tests.py

# Run comprehensive system test
python biodisc_core/comprehensive_system_test.py
```

## Documentation

- **CLAUDE.md**: Project guidance and development instructions
- **User_Manual/**: Detailed user manual
- **biodisc_core/docs/**: API documentation

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use BIODISC in your research, please cite:

```bibtex
@software{biodisc2026,
  title={BIODISC: Biology Discovery and Intelligence System},
  author={Tilanthi},
  year={2026},
  url={https://github.com/Tilanthi/BIODISC}
}
```

## Acknowledgments

BIODISC builds upon research in causal inference, meta-learning, swarm intelligence, and AGI architectures. Special thanks to the biological sciences community for domain expertise and feedback.
