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
"""Single-cell RNA-seq data connector.

Downloads scRNA-seq count matrices from public repositories (GEO supplementary
files or direct URLs), parses the common on-disk formats (CSV/TSV count
matrices, or 10x-style Matrix Market ``.mtx`` triplets with ``barcodes.tsv`` +
``features.tsv``), and runs a standard scanpy-equivalent preprocessing pipeline:

    1. drop genes expressed in fewer than ``min_cells_per_gene`` cells
    2. drop cells detecting fewer than ``min_genes_per_cell`` genes
    3. drop cells whose mitochondrial read fraction exceeds ``max_mito_percent``
    4. total-count normalize each cell to ``target_sum`` (default 10000)
    5. ``log1p`` transform

Implemented with numpy + pandas + scipy only. This connector does NOT depend on
``scanpy`` or ``anndata`` (both absent from the BIODISC environment); the scanpy
defaults are reproduced inline so downstream discovery code can consume real
scRNA-seq data without adding heavy dependencies.

OFFLINE TESTING: ``load(dry_run=True)`` synthesizes a sparse count matrix with
realistic mitochondrial genes, so the connector — and any code built on top of
it — can be unit-tested without network access. Discovery tests must use
``dry_run``; live network calls are reserved for production runs.

Reference return contract:

    expression_matrix : np.ndarray, shape (n_genes, n_cells), float64,
                        log-normalized (post-QC)
    gene_symbols      : List[str], length n_genes
    cell_labels       : List[str], length n_cells  (per-cell identity — barcodes
                        when available, else ``cell_0001``-style placeholders;
                        NOT cluster/cell-type labels unless supplied via the
                        ``cell_labels`` argument to ``load``)
"""

from __future__ import annotations

import gzip
import io
import logging
import re
import tarfile
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import requests
from scipy import sparse
from scipy.io import mmread

logger = logging.getLogger(__name__)


# Public type alias for the standard return contract (genes x cells, genes, cells).
ScRNAResult = Tuple[np.ndarray, List[str], List[str]]


# ---- scanpy-equivalent defaults ----
MIN_CELLS_PER_GENE: int = 3        # drop genes expressed in < this many cells
MIN_GENES_PER_CELL: int = 200      # drop cells detecting < this many genes
MAX_MITO_PERCENT: float = 20.0     # drop cells whose MT read fraction exceeds this (%)
TARGET_SUM: int = 10_000           # total-count normalization target

# Streamed-download bounds (mirror fixed_pipeline/geo_data_downloader.py).
_DEFAULT_CONNECT_TIMEOUT: int = 15
_DEFAULT_READ_TIMEOUT: int = 180
_DEFAULT_MAX_DOWNLOAD_BYTES: int = 2 * 1024 * 1024 * 1024  # 2 GB cap
_DEFAULT_MAX_DOWNLOAD_SECONDS: int = 600

# Mito gene prefix detection (handles human MT- and mouse mt- via uppercasing).
_MITO_PREFIXES: Tuple[str, ...] = ("MT-", "MT.")


# ============================================================================
# Small standalone helpers (module-level so they can be unit-tested directly)
# ============================================================================

def _looks_like_gene_symbol(s: object) -> bool:
    """Heuristic: does ``s`` look like a gene symbol?

    Gene symbols are short (<=15 chars), start with a letter, and contain only
    alphanumerics, dashes, underscores, or dots (e.g. ``GAPDH``, ``MT-CO1``,
    ``RP11-346K14.2``). Used for auto-detecting CSV orientation.
    """
    s = str(s).strip()
    if not s or len(s) > 15:
        return False
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9\-_.]*$", s))


def _gse_to_suppl_url(geo_id: str) -> str:
    """Return the GEO FTP supplementary-file directory URL for a GSE accession.

    GEO nests series under a parent folder whose name replaces the last three
    digits of the numeric part with ``nnn``: ``GSE12345`` lives under
    ``GSE12nnn/GSE12345``. Supplementary files (the raw uploads, including
    scRNA-seq ``.tar.gz`` bundles and ``.mtx`` files) sit under ``/suppl/``.
    """
    geo_id = geo_id.upper().strip()
    m = re.match(r"^GSE(\d+)$", geo_id)
    if not m:
        raise ValueError(
            f"Expected a GSE accession like 'GSE12345', got {geo_id!r}"
        )
    digits = m.group(1)
    # Zero-pad to >=4 digits so the parent folder is well-defined for tiny IDs.
    digits_padded = digits.zfill(4)
    parent = f"GSE{digits_padded[:-3]}nnn"
    return (
        "https://ftp.ncbi.nlm.nih.gov/geo/series/"
        f"{parent}/{geo_id}/suppl/"
    )


def _list_remote_files(url: str, timeout: Tuple[int, int]) -> List[str]:
    """List filenames at an Apache/nginx-style HTTP directory listing."""
    try:
        resp = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        logger.info(f"   directory listing failed for {url}: {e}")
        return []
    if resp.status_code != 200:
        logger.info(
            f"   directory listing returned status {resp.status_code} for {url}"
        )
        return []
    # Both Apache and nginx emit href="filename" for each entry.
    return re.findall(r'href="([^"/]+)"', resp.text)


def _stream_download(
    url: str,
    dest: Path,
    timeout: Tuple[int, int],
    max_bytes: int = _DEFAULT_MAX_DOWNLOAD_BYTES,
    max_seconds: int = _DEFAULT_MAX_DOWNLOAD_SECONDS,
) -> bool:
    """Stream a URL to ``dest`` with a hard byte + wall-clock bound.

    Returns True on success, False on any failure (status, network, deadline,
    size cap). Mirrors the bounded-download pattern in
    ``fixed_pipeline/geo_data_downloader.py`` — a plain ``response.content``
    read can hang indefinitely on a stalled half-open socket; bounding total
    time and bytes guarantees the call always returns.
    """
    start = time.monotonic()
    try:
        with requests.get(url, timeout=timeout, stream=True) as resp:
            if resp.status_code != 200:
                logger.info(f"   download {url} returned status {resp.status_code}")
                return False
            total = 0
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        logger.warning(
                            f"   {url} exceeds {max_bytes // (1024 * 1024)} MB cap, "
                            f"aborting download"
                        )
                        return False
                    if time.monotonic() - start > max_seconds:
                        logger.warning(
                            f"   {url} exceeded {max_seconds}s deadline, aborting"
                        )
                        return False
                    f.write(chunk)
        logger.info(
            f"   downloaded {dest.name} ({total // (1024 * 1024)} MB in "
            f"{time.monotonic() - start:.0f}s)"
        )
        return True
    except requests.exceptions.RequestException as e:
        logger.info(f"   download {url} failed: {e}")
        if dest.exists():
            try:
                dest.unlink()
            except OSError:
                pass
        return False


def _open_text(path: Path) -> io.TextIOBase:
    """Open a file for text reading, transparently decompressing ``.gz``."""
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")


def _parse_mtx_manual(path: Path) -> sparse.coo_matrix:
    """Parse a Matrix Market file by hand (fallback if ``scipy.io.mmread`` fails).

    Handles plain and gzip-compressed ``.mtx(.gz)`` files. Matrix Market is
    1-indexed and coordinate-formatted::

        %%MatrixMarket matrix coordinate real general
        n_rows n_cols n_nonzero
        row col value
        ...

    Returns a sparse COO matrix of shape ``(n_rows, n_cols)``.
    """
    rows: List[int] = []
    cols: List[int] = []
    vals: List[float] = []
    header_seen = False
    n_rows = n_cols = 0
    with _open_text(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if not header_seen:
                # First non-comment line: rows cols nnz
                n_rows, n_cols = int(parts[0]), int(parts[1])
                header_seen = True
                continue
            r, c, v = int(parts[0]), int(parts[1]), float(parts[2])
            rows.append(r - 1)  # MM is 1-indexed
            cols.append(c - 1)
            vals.append(v)
    return sparse.coo_matrix(
        (np.asarray(vals, dtype=float),
         (np.asarray(rows, dtype=np.int64), np.asarray(cols, dtype=np.int64))),
        shape=(n_rows, n_cols),
    )


def _read_features(path: Path) -> List[str]:
    """Read a 10x ``features.tsv`` (or ``genes.tsv``) file → list of gene symbols.

    cellranger v2/v3 lines are tab-separated with the gene symbol in column 2:
    ``ENSG00000139618 \t BRCA1 \t Gene Expression``. We fall back to column 1
    if only one column is present.
    """
    symbols: List[str] = []
    with _open_text(path) as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            parts = line.split("\t")
            symbols.append(parts[1] if len(parts) >= 2 else parts[0])
    return symbols


def _read_barcodes(path: Path) -> List[str]:
    """Read a 10x ``barcodes.tsv`` file → list of cell barcodes (one per line)."""
    with _open_text(path) as f:
        return [line.strip() for line in f if line.strip()]


def _pick_suppl_file(filenames: Sequence[str]) -> Tuple[str, str]:
    """Pick the most promising supplementary file from a GEO listing.

    Returns ``(filename, kind)`` where ``kind`` is one of
    ``'mtx_bundle' | 'mtx' | 'csv' | 'tsv'``. Returns ``("", "")`` if nothing
    scRNA-relevant is found. Ranking prefers 10x bundles and standalone
    ``.mtx`` files (the native scRNA-seq format) over flattened CSV/TSV.
    """
    scored: List[Tuple[str, str, int]] = []
    for fn in filenames:
        lower = fn.lower()
        if lower.endswith((".tar.gz", ".tgz")):
            boost = 0
            for kw in ("matrix", "raw", "10x", "scrna", "counts", "cellranger"):
                if kw in lower:
                    boost += 20
            scored.append((fn, "mtx_bundle", 80 + boost))
        elif lower.endswith((".mtx.gz", ".mtx")):
            scored.append((fn, "mtx", 90))
        elif lower.endswith((".csv.gz", ".csv")):
            boost = 10 if "count" in lower or "matrix" in lower else 0
            scored.append((fn, "csv", 50 + boost))
        elif lower.endswith((".tsv.gz", ".tsv")):
            boost = 10 if "count" in lower or "matrix" in lower else 0
            scored.append((fn, "tsv", 40 + boost))
    if not scored:
        return "", ""
    scored.sort(key=lambda x: -x[2])
    return scored[0][0], scored[0][1]


# ============================================================================
# Preprocessing — the scanpy-equivalent core (public, reusable)
# ============================================================================

def scanpy_like_preprocess(
    matrix: np.ndarray,
    gene_symbols: Sequence[str],
    cell_labels: Sequence[str],
    min_cells_per_gene: int = MIN_CELLS_PER_GENE,
    min_genes_per_cell: int = MIN_GENES_PER_CELL,
    max_mito_percent: float = MAX_MITO_PERCENT,
    target_sum: int = TARGET_SUM,
    inplace: bool = False,
) -> ScRNAResult:
    """Run the standard scanpy preprocessing pipeline on a raw count matrix.

    Implemented with numpy only. Operates on a genes × cells matrix of raw
    integer counts (the output of 10x/CITE-seq/Smart-seq pipelines). Steps:

        1. gene filter  — keep genes expressed (>0) in >= ``min_cells_per_gene`` cells
        2. cell filter  — keep cells detecting >= ``min_genes_per_cell`` genes
        3. mito filter  — keep cells whose MT-read fraction <= ``max_mito_percent``
        4. normalize    — scale each cell's total to ``target_sum``
        5. log1p        — ``np.log1p`` transform

    A mitochondrial gene is any gene whose symbol (uppercased) starts with one
    of ``_MITO_PREFIXES`` (``MT-`` covers human ``MT-CO1`` and mouse ``mt-Co1``
    alike; ``MT.`` is a rarer alternative delimiter).

    Args:
        matrix: ``(n_genes, n_cells)`` raw count matrix (will be cast to float64).
        gene_symbols: length-``n_genes`` gene identifiers.
        cell_labels: length-``n_cells`` per-cell identity strings.
        min_cells_per_gene: minimum number of cells expressing a gene for it to be kept.
        min_genes_per_cell: minimum number of genes detected in a cell for it to be kept.
        max_mito_percent: maximum mitochondrial read percentage (0-100) per cell.
        target_sum: total-count normalization target (scanpy default 10000).
        inplace: when True, mutate the input ``matrix``/lists where possible
            (still returns the filtered views for clarity).

    Returns:
        ``(expression_matrix, gene_symbols, cell_labels)`` — log-normalized,
        post-QC, with consistent shapes/lengths.
    """
    M = np.asarray(matrix, dtype=np.float64) if not inplace else matrix.astype(
        np.float64, copy=False
    )
    genes: List[str] = list(gene_symbols)
    cells: List[str] = list(cell_labels)

    if M.ndim != 2:
        raise ValueError(
            f"expected a 2-D (genes x cells) matrix, got shape {M.shape}"
        )
    if M.shape[0] != len(genes):
        raise ValueError(
            f"matrix has {M.shape[0]} rows but gene_symbols has {len(genes)} entries"
        )
    if M.shape[1] != len(cells):
        raise ValueError(
            f"matrix has {M.shape[1]} cols but cell_labels has {len(cells)} entries"
        )

    # Step 1 — gene filter: genes expressed in >= min_cells_per_gene cells.
    cells_per_gene = (M > 0).sum(axis=1)
    keep_genes = cells_per_gene >= min_cells_per_gene
    n_genes_before = M.shape[0]
    M = M[keep_genes]
    genes = [g for g, k in zip(genes, keep_genes) if k]
    logger.info(
        f"   gene filter: kept {M.shape[0]}/{n_genes_before} genes "
        f"(>= {min_cells_per_gene} cells)"
    )

    # Step 2 — cell filter: cells detecting >= min_genes_per_cell genes.
    genes_per_cell = (M > 0).sum(axis=0)
    keep_cells = genes_per_cell >= min_genes_per_cell
    n_cells_before = M.shape[1]
    M = M[:, keep_cells]
    cells = [c for c, k in zip(cells, keep_cells) if k]
    logger.info(
        f"   cell filter: kept {M.shape[1]}/{n_cells_before} cells "
        f"(>= {min_genes_per_cell} genes)"
    )

    if M.shape[1] == 0 or M.shape[0] == 0:
        raise ValueError(
            "preprocessing emptied the matrix — QC thresholds are too strict "
            "for this dataset (lower min_cells_per_gene / min_genes_per_cell)"
        )

    # Step 3 — mitochondrial filter: drop high-mito cells.
    mito_mask = np.array(
        [str(g).upper().startswith(_MITO_PREFIXES) for g in genes],
        dtype=bool,
    )
    if mito_mask.any():
        mito_counts = M[mito_mask].sum(axis=0)
        total_counts = M.sum(axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            mito_pct = np.where(
                total_counts > 0,
                mito_counts / total_counts * 100.0,
                0.0,
            )
        keep_cells = mito_pct <= max_mito_percent
        n_before_mito = M.shape[1]
        M = M[:, keep_cells]
        cells = [c for c, k in zip(cells, keep_cells) if k]
        logger.info(
            f"   mito filter: kept {M.shape[1]}/{n_before_mito} cells "
            f"(<= {max_mito_percent}% MT; {int(mito_mask.sum())} MT genes detected)"
        )
    else:
        logger.info("   mito filter: no MT- genes found — skipping mito QC")

    if M.shape[1] == 0:
        raise ValueError(
            "all cells dropped by mitochondrial filter — check gene naming or "
            "raise max_mito_percent"
        )

    # Step 4 — total-count normalize each cell to target_sum.
    counts_per_cell = M.sum(axis=0)
    # Guard against divide-by-zero (shouldn't happen post-cell-filter, but safe).
    scale = np.where(
        counts_per_cell > 0, target_sum / counts_per_cell, 0.0
    )
    M = M * scale[np.newaxis, :]

    # Step 5 — log1p transform.
    M = np.log1p(M)

    logger.info(
        f"   normalized: final matrix {M.shape[0]} genes x {M.shape[1]} cells "
        f"(target_sum={target_sum}, log1p)"
    )
    return M, genes, cells


# ============================================================================
# Main connector
# ============================================================================

class ScRNASeqConnector:
    """Connector that fetches, parses, and preprocesses scRNA-seq count data.

    The connector accepts a dataset from one of four sources (in priority order):

        1. ``dry_run=True``          — synthesize a sparse count matrix offline.
        2. ``path=`` (a local file)  — parse a CSV/TSV/.mtx/.tar.gz directly.
        3. ``url=``                  — download then parse (any of the above).
        4. ``geo_id=``               — resolve via the GEO FTP ``/suppl/`` folder.

    After parsing, the raw counts flow through :func:`scanpy_like_preprocess`
    unless ``preprocess=False``.

    Example (offline):
        >>> from biodisc_core.breakthrough.connectors import (
        ...     create_scrnaseq_connector,
        ... )
        >>> c = create_scrnaseq_connector()
        >>> mat, genes, cells = c.load(dry_run=True)
        >>> mat.shape[0] == len(genes)
        True

    Example (GEO):
        >>> mat, genes, cells = c.load(geo_id="GSE144236")

    Network failures (DNS, timeouts, HTTP errors, malformed files) are logged
    and surface as ``None`` from :meth:`load` — they never raise, so the
    discovery loop can skip a broken dataset and continue.
    """

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        timeout: Union[int, Tuple[int, int]] = (
            _DEFAULT_CONNECT_TIMEOUT,
            _DEFAULT_READ_TIMEOUT,
        ),
        max_download_bytes: int = _DEFAULT_MAX_DOWNLOAD_BYTES,
        max_download_seconds: int = _DEFAULT_MAX_DOWNLOAD_SECONDS,
    ) -> None:
        """Configure download cache and timeouts.

        Args:
            cache_dir: directory for downloaded files (defaults to a
                ``biodisc_scrna`` subfolder of the system temp dir).
            timeout: per-request ``(connect, read)`` timeout tuple. If an int
                is passed it is used as both connect and read timeout.
            max_download_bytes: hard cap on a single streamed download.
            max_download_seconds: hard wall-clock cap on a single download.
        """
        self.cache_dir = Path(cache_dir) if cache_dir else (
            Path(tempfile.gettempdir()) / "biodisc_scrna"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(timeout, int):
            timeout = (timeout, timeout)
        self.timeout: Tuple[int, int] = timeout
        self.max_download_bytes = max_download_bytes
        self.max_download_seconds = max_download_seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(
        self,
        geo_id: Optional[str] = None,
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
        n_genes_dry: int = 1000,
        n_cells_dry: int = 500,
        seed: int = 0,
        cell_labels: Optional[Sequence[str]] = None,
        preprocess: bool = True,
        min_cells_per_gene: int = MIN_CELLS_PER_GENE,
        min_genes_per_cell: int = MIN_GENES_PER_CELL,
        max_mito_percent: float = MAX_MITO_PERCENT,
        target_sum: int = TARGET_SUM,
    ) -> Optional[ScRNAResult]:
        """Load an scRNA-seq count matrix and (optionally) preprocess it.

        Provide exactly one of ``dry_run``, ``path``, ``url``, ``geo_id``
        (``dry_run`` wins if multiple are set).

        Args:
            geo_id: GEO series accession (e.g. ``GSE12345``).
            url: direct URL to a count matrix or 10x bundle (``.tar.gz`` /
                ``.mtx(.gz)`` / ``.csv(.gz)`` / ``.tsv(.gz)``).
            path: local path to one of the same file types.
            dry_run: synthesize a sparse count matrix (offline test mode).
            n_genes_dry, n_cells_dry, seed: synthetic-data parameters
                (only used when ``dry_run=True``).
            cell_labels: optional per-cell labels to use INSTEAD of barcodes /
                placeholders (e.g. known cell-type annotations). Length must
                match the number of cells in the parsed matrix. Ignored in
                ``dry_run`` mode.
            preprocess: if True, run :func:`scanpy_like_preprocess` on the
                parsed raw counts; if False, return raw counts unchanged.
            min_cells_per_gene, min_genes_per_cell, max_mito_percent, target_sum:
                forwarded to the preprocessing pipeline (scanpy defaults).

        Returns:
            ``(expression_matrix, gene_symbols, cell_labels)`` or ``None`` if
            the dataset could not be fetched or parsed.
        """
        try:
            if dry_run:
                raw = self._generate_synthetic(
                    n_genes=n_genes_dry, n_cells=n_cells_dry, seed=seed
                )
            elif path is not None:
                raw = self._parse_local_path(Path(path))
            elif url is not None:
                raw = self._load_from_url(url)
            elif geo_id is not None:
                raw = self._load_from_geo(geo_id)
            else:
                raise ValueError(
                    "load() requires one of dry_run, path, url, or geo_id"
                )
        except Exception as e:
            # Any unexpected error is logged and surfaced as None so the
            # discovery loop can keep going. Invalid arguments above still
            # raise (ValueError) because they are programmer errors.
            logger.warning(f"scrna_connector.load failed: {e}")
            return None

        if raw is None:
            return None

        matrix, gene_symbols, parsed_cells = raw

        # Override cell labels if caller supplied annotations.
        if cell_labels is not None:
            if len(cell_labels) != len(parsed_cells):
                logger.warning(
                    f"cell_labels has {len(cell_labels)} entries but matrix "
                    f"has {len(parsed_cells)} cells — ignoring override"
                )
            else:
                parsed_cells = list(cell_labels)

        if preprocess:
            return scanpy_like_preprocess(
                matrix,
                gene_symbols,
                parsed_cells,
                min_cells_per_gene=min_cells_per_gene,
                min_genes_per_cell=min_genes_per_cell,
                max_mito_percent=max_mito_percent,
                target_sum=target_sum,
            )
        return matrix, list(gene_symbols), list(parsed_cells)

    # ------------------------------------------------------------------
    # Source resolution
    # ------------------------------------------------------------------

    def _load_from_geo(self, geo_id: str) -> Optional[ScRNAResult]:
        """Resolve and parse a GEO series' scRNA-seq supplementary files."""
        suppl_url = _gse_to_suppl_url(geo_id)
        logger.info(f"🌐 GEO {geo_id}: listing {suppl_url}")
        files = _list_remote_files(suppl_url, self.timeout)
        if not files:
            logger.warning(f"   no supplementary files found at {suppl_url}")
            return None

        fname, kind = _pick_suppl_file(files)
        if not fname:
            logger.warning(
                f"   no scRNA-relevant file among {len(files)} supplementary "
                f"files for {geo_id}"
            )
            return None
        logger.info(f"   picked '{fname}' (kind={kind})")

        local = self.cache_dir / fname
        url = suppl_url + fname
        if not _stream_download(
            url,
            local,
            self.timeout,
            max_bytes=self.max_download_bytes,
            max_seconds=self.max_download_seconds,
        ):
            return None

        return self._parse_local_path(local, kind_hint=kind)

    def _load_from_url(self, url: str) -> Optional[ScRNAResult]:
        """Download then parse a single URL."""
        fname = url.rstrip("/").split("/")[-1] or "download"
        local = self.cache_dir / fname
        logger.info(f"🌐 downloading {url}")
        if not _stream_download(
            url,
            local,
            self.timeout,
            max_bytes=self.max_download_bytes,
            max_seconds=self.max_download_seconds,
        ):
            return None
        return self._parse_local_path(local)

    # ------------------------------------------------------------------
    # Parsing — dispatches on file type
    # ------------------------------------------------------------------

    def _parse_local_path(
        self,
        path: Path,
        kind_hint: str = "",
    ) -> Optional[ScRNAResult]:
        """Parse a local file, dispatching on extension / hint.

        Args:
            path: file to parse.
            kind_hint: optional pre-classified kind (``'mtx_bundle'``,
                ``'mtx'``, ``'csv'``, ``'tsv'``); bypasses extension sniffing
                when GEO listing already identified the file.
        """
        path = Path(path)
        if not path.exists():
            logger.warning(f"   file does not exist: {path}")
            return None

        name = path.name.lower()
        kind = kind_hint
        if not kind:
            if name.endswith((".tar.gz", ".tgz")):
                kind = "mtx_bundle"
            elif name.endswith((".mtx.gz", ".mtx")):
                kind = "mtx"
            elif name.endswith((".csv.gz", ".csv")):
                kind = "csv"
            elif name.endswith((".tsv.gz", ".tsv")):
                kind = "tsv"
            else:
                logger.warning(f"   unrecognized file type: {path.name}")
                return None

        if kind == "mtx_bundle":
            return self._parse_mtx_bundle(path)
        if kind == "mtx":
            return self._parse_mtx_alone(path)
        if kind in ("csv", "tsv"):
            return self._parse_csv_tsv(path, kind)
        logger.warning(f"   unsupported kind '{kind}' for {path.name}")
        return None

    def _parse_mtx_bundle(self, tar_path: Path) -> Optional[ScRNAResult]:
        """Extract a 10x tarball and parse its matrix.mtx + barcodes + features."""
        extract_dir = self.cache_dir / (
            tar_path.stem + "_extracted_" + str(int(time.time()))
        )
        extract_dir.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(tar_path, "r:*") as tar:
                # ``filter="data"`` (Py3.12+) blocks path-traversal members.
                try:
                    tar.extractall(extract_dir, filter="data")
                except TypeError:
                    tar.extractall(extract_dir)
        except (tarfile.TarError, OSError) as e:
            logger.warning(f"   tar extraction failed for {tar_path.name}: {e}")
            return None

        mtx = self._find_in_tree(extract_dir, r"matrix.*\.mtx(?:\.gz)?$")
        barcodes = self._find_in_tree(extract_dir, r"barcodes?\.tsv(?:\.gz)?$")
        features = self._find_in_tree(
            extract_dir, r"(?:features|genes)\.tsv(?:\.gz)?$"
        )

        if mtx is None:
            logger.warning(
                f"   no matrix.mtx found inside bundle {tar_path.name}"
            )
            return None

        return self._assemble_mtx(mtx, features, barcodes)

    def _parse_mtx_alone(self, mtx_path: Path) -> Optional[ScRNAResult]:
        """Parse a standalone ``.mtx(.gz)`` file (no barcodes/features expected).

        If sibling ``barcodes.tsv`` / ``features.tsv`` files sit next to the
        matrix they are picked up automatically; otherwise gene/cell labels are
        generated as placeholders.
        """
        sibling = mtx_path.parent
        # A 10x folder typically names them exactly barcodes.tsv(.gz) etc.
        barcodes = self._find_sibling(sibling, r"barcodes?\.tsv(?:\.gz)?$")
        features = self._find_sibling(
            sibling, r"(?:features|genes)\.tsv(?:\.gz)?$"
        )
        return self._assemble_mtx(mtx_path, features, barcodes)

    def _assemble_mtx(
        self,
        mtx_path: Path,
        features_path: Optional[Path],
        barcodes_path: Optional[Path],
    ) -> Optional[ScRNAResult]:
        """Read a sparse ``.mtx`` plus optional features/barcodes into a dense matrix.

        10x Matrix Market output is ``(n_features, n_cells)`` — i.e. already
        genes × cells, matching the return contract. The matrix is densified
        here; for very large datasets (>50k cells) consider filtering before
        densification (a future sparse-aware path).
        """
        try:
            M = mmread(str(mtx_path))  # scipy.io.mmread — handles .gz transparently
        except Exception as e:
            logger.info(
                f"   scipy.io.mmread failed on {mtx_path.name} ({e}); "
                f"falling back to manual parser"
            )
            try:
                M = _parse_mtx_manual(mtx_path)
            except Exception as e2:
                logger.warning(
                    f"   manual mtx parse also failed on {mtx_path.name}: {e2}"
                )
                return None

        if sparse.issparse(M):
            M = M.toarray()
        M = np.asarray(M, dtype=np.float64)

        if features_path is not None:
            gene_symbols = _read_features(features_path)
        else:
            gene_symbols = [f"gene_{i:05d}" for i in range(M.shape[0])]
        if barcodes_path is not None:
            cell_labels = _read_barcodes(barcodes_path)
        else:
            cell_labels = [f"cell_{i:05d}" for i in range(M.shape[1])]

        # Shape reconciliation — defend against truncated feature/barcode files.
        if len(gene_symbols) != M.shape[0]:
            logger.warning(
                f"   features count ({len(gene_symbols)}) != matrix rows "
                f"({M.shape[0]}); truncating/padding gene symbols"
            )
            gene_symbols = self._reconcile_labels(gene_symbols, M.shape[0], "gene")
        if len(cell_labels) != M.shape[1]:
            logger.warning(
                f"   barcodes count ({len(cell_labels)}) != matrix cols "
                f"({M.shape[1]}); truncating/padding cell labels"
            )
            cell_labels = self._reconcile_labels(cell_labels, M.shape[1], "cell")

        logger.info(
            f"   parsed mtx: {M.shape[0]} genes x {M.shape[1]} cells "
            f"({int((M > 0).sum())} non-zero entries)"
        )
        return M, gene_symbols, cell_labels

    def _parse_csv_tsv(
        self,
        path: Path,
        kind: str,
    ) -> Optional[ScRNAResult]:
        """Parse a flat CSV or TSV count matrix into a genes × cells array.

        Orientation is auto-detected: if the row index looks more gene-like
        than the column header (sampled heuristically), the file is treated as
        genes × cells; otherwise it is transposed. This handles both the Seurat
        convention (genes in rows) and the AnnData convention (cells in rows).
        """
        sep = "\t" if kind == "tsv" else ","
        try:
            df = pd.read_csv(
                path,
                sep=sep,
                index_col=0,
                compression="infer",
            )
        except Exception as e:
            logger.warning(f"   pandas failed to parse {path.name}: {e}")
            return None

        if df.empty:
            logger.warning(f"   parsed dataframe is empty: {path.name}")
            return None

        # Auto-detect orientation.
        genes_as_rows = self._genes_in_rows(df)
        if not genes_as_rows:
            df = df.T

        gene_symbols = [str(s) for s in df.index]
        cell_labels = [str(s) for s in df.columns]
        matrix = df.to_numpy(dtype=np.float64)
        logger.info(
            f"   parsed {kind.upper()}: {matrix.shape[0]} genes x "
            f"{matrix.shape[1]} cells from {path.name}"
        )
        return matrix, gene_symbols, cell_labels

    # ------------------------------------------------------------------
    # Synthetic data (dry_run)
    # ------------------------------------------------------------------

    def _generate_synthetic(
        self,
        n_genes: int = 1000,
        n_cells: int = 500,
        seed: int = 0,
    ) -> ScRNAResult:
        """Generate a realistic sparse count matrix for offline testing.

        Produces raw integer counts (not normalized) with ~30% non-zero
        entries, plus 10 ``MT-*`` mitochondrial genes whose expression is
        elevated in ~15% of cells — enough to exercise every branch of the
        preprocessing pipeline (gene filter, cell filter, mito filter,
        normalize, log1p) without network access.
        """
        rng = np.random.default_rng(seed)

        # Regular genes: mostly zero, occasional Poisson(1) counts.
        counts = rng.poisson(lam=0.4, size=(n_genes, n_cells)).astype(np.float64)
        # Ensure at least a few genes are broadly expressed (housekeeping-like)
        # so the min_cells_per_gene filter doesn't drop everything.
        housekeeping = rng.choice(n_genes, size=max(5, n_genes // 50), replace=False)
        counts[housekeeping] += rng.poisson(
            lam=20.0, size=(len(housekeeping), n_cells)
        ).astype(np.float64)

        # MT- genes: 10 rows, generally high expression; ~15% of cells get a
        # 5x boost to push them over the 20% mito cutoff and test the filter.
        n_mt = 10
        mt_counts = rng.poisson(
            lam=40.0, size=(n_mt, n_cells)
        ).astype(np.float64)
        high_mito = rng.choice(
            n_cells, size=max(1, int(0.15 * n_cells)), replace=False
        )
        mt_counts[:, high_mito] *= 5.0

        regular_symbols = [f"GENE_{i:05d}" for i in range(n_genes)]
        mt_symbols = [f"MT-{c}" for c in "ABCDEFGHIJ"]
        all_symbols = regular_symbols + mt_symbols

        full = np.vstack([counts, mt_counts])
        cell_labels = [f"cell_{i:05d}" for i in range(n_cells)]

        logger.info(
            f"   [dry_run] synthesized {full.shape[0]} genes x {full.shape[1]} "
            f"cells (seed={seed}); {int((full > 0).mean() * 100)}% non-zero, "
            f"{n_mt} MT- genes injected"
        )
        return full, all_symbols, cell_labels

    # ------------------------------------------------------------------
    # Small private utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _find_in_tree(root: Path, pattern: str) -> Optional[Path]:
        """Case-insensitive regex search for a file under ``root``."""
        rx = re.compile(pattern, re.IGNORECASE)
        for p in root.rglob("*"):
            if p.is_file() and rx.search(p.name):
                return p
        return None

    @staticmethod
    def _find_sibling(directory: Path, pattern: str) -> Optional[Path]:
        """Case-insensitive regex search among immediate children of a directory."""
        rx = re.compile(pattern, re.IGNORECASE)
        for p in directory.iterdir():
            if p.is_file() and rx.search(p.name):
                return p
        return None

    @staticmethod
    def _genes_in_rows(df: pd.DataFrame) -> bool:
        """Decide whether a parsed DataFrame's rows are genes (True) or cells.

        Heuristic: sample up to 20 row labels and 20 column labels; whichever
        side has more gene-symbol-like strings is the gene axis. Falls back to
        "genes in rows" on a tie, which is the more common convention.
        """
        n = min(20, len(df.index), len(df.columns))
        if n == 0:
            return True
        row_score = sum(
            _looks_like_gene_symbol(s) for s in list(df.index)[:n]
        )
        col_score = sum(
            _looks_like_gene_symbol(s) for s in list(df.columns)[:n]
        )
        return row_score >= col_score

    @staticmethod
    def _reconcile_labels(
        labels: List[str], expected: int, prefix: str
    ) -> List[str]:
        """Truncate or pad ``labels`` to length ``expected``.

        Truncation drops the tail; padding appends ``f"{prefix}_{i}"`` entries
        so downstream shape checks pass even if a features/barcodes file was
        truncated on disk.
        """
        if len(labels) > expected:
            return labels[:expected]
        if len(labels) < expected:
            labels = list(labels) + [
                f"{prefix}_{i:05d}" for i in range(len(labels), expected)
            ]
        return labels


def create_scrnaseq_connector(
    cache_dir: Optional[Union[str, Path]] = None,
    timeout: Union[int, Tuple[int, int]] = (
        _DEFAULT_CONNECT_TIMEOUT,
        _DEFAULT_READ_TIMEOUT,
    ),
) -> ScRNASeqConnector:
    """Factory: create an :class:`ScRNASeqConnector` (preferred over direct ctor).

    Mirrors the factory-function convention used throughout ``biodisc_core``
    (e.g. ``create_geo_data_downloader``).
    """
    return ScRNASeqConnector(cache_dir=cache_dir, timeout=timeout)


# Module-level singleton so the convenience function below can reuse a single
# connector (and its on-disk cache) across calls without forcing callers to
# instantiate a class.
_DEFAULT_CONNECTOR: Optional[ScRNASeqConnector] = None


def _get_default_connector() -> ScRNASeqConnector:
    global _DEFAULT_CONNECTOR
    if _DEFAULT_CONNECTOR is None:
        _DEFAULT_CONNECTOR = create_scrnaseq_connector()
    return _DEFAULT_CONNECTOR


def fetch_scrnaseq_expression(
    geo_id: Optional[str] = None,
    url: Optional[str] = None,
    path: Optional[Union[str, Path]] = None,
    dry_run: bool = False,
    preprocess: bool = True,
    **kwargs,
) -> Optional[ScRNAResult]:
    """Module-level convenience wrapper — see :meth:`ScRNASeqConnector.load`.

    Mirrors :func:`biodisc_core.breakthrough.connectors.fetch_tcga_expression`:
    builds (or reuses) a default :class:`ScRNASeqConnector` and delegates to its
    ``load`` method, so callers can fetch a single dataset without managing a
    connector instance.

    Example:
        >>> from biodisc_core.breakthrough.connectors import (
        ...     fetch_scrnaseq_expression,
        ... )
        >>> mat, genes, cells = fetch_scrnaseq_expression(dry_run=True)
    """
    return _get_default_connector().load(
        geo_id=geo_id,
        url=url,
        path=path,
        dry_run=dry_run,
        preprocess=preprocess,
        **kwargs,
    )
