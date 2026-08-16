# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""External data connectors for the breakthrough discovery package.

Each connector adapts a specific public bioinformatics repository (TCGA/GDC,
GEO, ArrayExpress, GTEx, AlphaFold, ...) to a standard tuple shape consumed by
the breakthrough discovery candidate generators.

Bulk RNA-seq connectors (TCGA, GEO bulk) target the differential-expression
contract::

    (expression_matrix, gene_symbols, group_labels)

    expression_matrix : np.ndarray, shape (n_genes, n_samples), float
    gene_symbols      : List[str], length n_genes
    group_labels      : np.ndarray, length n_samples, 0=normal / 1=tumor

so any bulk connector can be swapped into the existing
``DifferentialExpressionAnalyzer.perform_differential_expression_analysis``
pipeline without changes downstream.

The AlphaFold connector is a structure/confidence connector (per-residue pLDDT
-> disorder profile) rather than an expression connector, so it does not emit
the DE tuple. It answers the re-mining novel question about shared disordered
regions across protein families.

The scRNA-seq connector emits a single-cell variant of the DE tuple — cells do
not carry a binary tumor/normal split, so the third element is per-cell
identity (barcodes or placeholders), and the matrix is log-normalized post-QC::

    (expression_matrix, gene_symbols, cell_labels)

    expression_matrix : np.ndarray, shape (n_genes, n_cells), float, log-normalized
    gene_symbols      : List[str], length n_genes
    cell_labels       : List[str], length n_cells
"""

from .tcga_connector import (
    TCGAConnector,
    create_tcga_connector,
    fetch_tcga_expression,
)

from .alphafold_connector import (
    AlphaFoldConnector,
    CrossProteinComparison,
    DomainAnnotation,
    ProteinDisorderProfile,
    Region,
    ResidueConfidence,
    SharedDisorderPattern,
    create_alphafold_connector,
    get_alphafold_connector,
)

from .scrna_connector import (
    MAX_MITO_PERCENT,
    MIN_CELLS_PER_GENE,
    MIN_GENES_PER_CELL,
    TARGET_SUM,
    ScRNAResult,
    ScRNASeqConnector,
    create_scrnaseq_connector,
    fetch_scrnaseq_expression,
    scanpy_like_preprocess,
)

__all__ = [
    # TCGA / bulk RNA-seq
    "TCGAConnector",
    "create_tcga_connector",
    "fetch_tcga_expression",
    # AlphaFold / structure
    "AlphaFoldConnector",
    "CrossProteinComparison",
    "DomainAnnotation",
    "ProteinDisorderProfile",
    "Region",
    "ResidueConfidence",
    "SharedDisorderPattern",
    "create_alphafold_connector",
    "get_alphafold_connector",
    # scRNA-seq / single cell
    "ScRNASeqConnector",
    "create_scrnaseq_connector",
    "fetch_scrnaseq_expression",
    "scanpy_like_preprocess",
    "ScRNAResult",
    "MIN_CELLS_PER_GENE",
    "MIN_GENES_PER_CELL",
    "MAX_MITO_PERCENT",
    "TARGET_SUM",
]
