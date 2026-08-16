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
"""
TCGA / GDC Data Connector.

Queries the NCI Genomic Data Commons (GDC) REST API
(https://api.gdc.cancer.gov/) for TCGA RNA-seq datasets and returns a
(genes x samples) expression matrix with binary tumor/normal labels in the
exact shape BIODISC's existing differential-expression pipeline consumes::

    (expression_matrix, gene_symbols, group_labels)

    expression_matrix : np.ndarray, shape (n_genes, n_samples), float
    gene_symbols      : List[str], length n_genes
    group_labels      : np.ndarray, length n_samples, 0=normal / 1=tumor

This is the TCGA analogue of ``fixed_pipeline/geo_data_downloader.py`` and is
intended to slot into the same downstream analyzer
(``DifferentialExpressionAnalyzer.perform_differential_expression_analysis``)
without modification.

OFFLINE TESTING
---------------
Pass ``dry_run=True`` to :meth:`TCGAConnector.fetch_expression` (or the
module-level :func:`fetch_tcga_expression`) to obtain synthetic-shaped,
pipeline-compatible data with **no** network access. Real downloads hit
``api.gdc.cancer.gov`` and require connectivity.

GDC API WORKFLOW
----------------
1. ``POST /files`` with a filter (``cases.project.project_id`` =
   ``'TCGA-BRCA'``, ``data_type`` = ``'Gene Expression Quantification'``,
   ``analysis.workflow_type`` = ``'STAR - Counts'``, ``cases.samples.sample_type``
   = ``'Primary Tumor'`` / ``'Solid Tissue Normal'``) to list RNA-seq file UUIDs.
2. ``GET /data/{file_id}`` for each file UUID to download the tab-separated
   gene-expression file.
3. Parse each file and build a ``(genes x samples)`` matrix with HGNC symbols
   as row labels (``STAR - Counts`` files include a ``gene_name`` column; legacy
   ``HTSeq - FPKM`` / ``HTSeq - Counts`` files expose only Ensembl IDs and are
   returned with Ensembl IDs as the "symbol").

A single file corresponds to exactly one sample (one aliquot), and is either
tumor or normal — never both. The connector therefore issues two /files
queries (one per sample-type class) and concatenates the columns, emitting
labels ``[1]*n_tumor + [0]*n_normal``.
"""

from __future__ import annotations

import gzip
import io
import json
import logging
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GDC API endpoints and defaults
# ---------------------------------------------------------------------------
GDC_BASE_URL: str = "https://api.gdc.cancer.gov"
FILES_ENDPOINT: str = f"{GDC_BASE_URL}/files"
DATA_ENDPOINT: str = f"{GDC_BASE_URL}/data"

_DEFAULT_HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# GDC "cases.samples.sample_type" vocabulary. A single file maps to one of
# these. We split into tumor vs normal buckets so the DE pipeline gets a real
# case/control contrast — never a fabricated split.
TUMOR_SAMPLE_TYPES: Tuple[str, ...] = (
    "Primary Tumor",
    "Recurrent Solid Tumor",
    "Metastatic",
)
NORMAL_SAMPLE_TYPES: Tuple[str, ...] = (
    "Solid Tissue Normal",
    "Blood Derived Normal",
    "Bone Marrow Normal",
    "Adjacent Normal",
)

# Fields requested from /files so we can identify the sample type and workflow
# without a second round-trip.
_FILE_FIELDS: Tuple[str, ...] = (
    "file_id",
    "file_name",
    "file_size",
    "data_type",
    "data_category",
    "experimental_strategy",
    "analysis.workflow_type",
    "access",
    "cases.submitter_id",
    "cases.samples.sample_type",
    "cases.samples.portion_number",
    "cases.project.project_id",
)

# HTSeq summary rows that are not real genes — drop them when parsing legacy
# 2-column HTSeq files.
_HTSEQ_SUMMARY_IDS: frozenset = frozenset(
    {
        "__no_feature",
        "__ambiguous",
        "__too_low_aQual",
        "__not_aligned",
        "__alignment_not_unique",
    }
)

# Gene types retained when parsing STAR - Counts files. Default keeps only
# protein-coding genes so the row set matches what BIODISC's gene-symbol gate
# expects; pass a wider tuple to include lncRNAs etc.
_DEFAULT_GENE_TYPES: Tuple[str, ...] = ("protein_coding",)


class GDCAPIError(RuntimeError):
    """Raised on unrecoverable GDC API failures (after retries are exhausted)."""


# ---------------------------------------------------------------------------
# Cancer-type normalization
# ---------------------------------------------------------------------------
def _normalize_project_id(cancer_type: str) -> str:
    """Normalize a user-supplied cancer type to a TCGA project_id.

    Accepts ``'BRCA'``, ``'brca'``, or ``'TCGA-BRCA'`` and returns the canonical
    ``'TCGA-BRCA'`` form used by the GDC ``cases.project.project_id`` field.
    """
    ct = cancer_type.strip().upper()
    if not ct:
        raise ValueError("cancer_type must be a non-empty string (e.g. 'BRCA')")
    if ct.startswith("TCGA-"):
        return ct
    if "-" in ct and ct.split("-")[0] == "TCGA":
        return ct
    return f"TCGA-{ct}"


def _default_value_column(workflow_type: str) -> str:
    """Pick a sensible default expression column for a GDC workflow_type."""
    wf = workflow_type.strip()
    if wf == "STAR - Counts":
        # Multi-column file; FPKM is comparable across genes (unlike raw counts
        # without a size factor). TPM is the alternative.
        return "fpkm_unstranded"
    if wf == "HTSeq - FPKM":
        return "FPKM"
    if wf == "HTSeq - Counts":
        return "unstranded"
    # Unknown workflow — assume the modern STAR format.
    logger.warning(
        "Unknown GDC workflow_type %r; defaulting value column to 'fpkm_unstranded'",
        workflow_type,
    )
    return "fpkm_unstranded"


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------
class TCGAConnector:
    """Download TCGA RNA-seq data from the GDC API as a DE-pipeline tuple.

    The connector is stateless across calls (a small in-memory file_id -> bytes
    cache is kept only to avoid re-downloading within a single process when a
    caller retries). It is safe to instantiate once and reuse.

    Parameters
    ----------
    base_url, files_endpoint, data_endpoint
        Override the GDC host (useful for tests against a local mock).
    timeout
        Per-request timeout in seconds (connect+read combined).
    max_retries
        Number of retry attempts on transient failures (timeouts, 429, 5xx).
    backoff
        Base for exponential backoff: wait ``backoff * 2**attempt`` seconds.
    sleep_between_downloads
        Polite delay between successive ``/data`` GETs to avoid hammering GDC.
    user_agent
        Sent as the ``User-Agent`` header (GDC requests a identifying UA).
    """

    def __init__(
        self,
        base_url: str = GDC_BASE_URL,
        files_endpoint: Optional[str] = None,
        data_endpoint: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        backoff: float = 2.0,
        sleep_between_downloads: float = 0.5,
        user_agent: str = "BIODISC-TCGA-Connector/1.0",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.files_endpoint = files_endpoint or f"{self.base_url}/files"
        self.data_endpoint = data_endpoint or f"{self.base_url}/data"
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.sleep_between_downloads = sleep_between_downloads
        self.headers = {**_DEFAULT_HEADERS, "User-Agent": user_agent}
        # Small in-memory cache: file_id -> raw bytes. Prevents duplicate
        # downloads when a caller retries the same cancer type.
        self._cache: Dict[str, bytes] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def fetch_expression(
        self,
        cancer_type: str,
        n_tumor: int = 20,
        n_normal: int = 20,
        workflow_type: str = "STAR - Counts",
        value_column: Optional[str] = None,
        gene_types: Sequence[str] = _DEFAULT_GENE_TYPES,
        max_genes: int = 2000,
        dry_run: bool = False,
        random_state: int = 42,
    ) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
        """Fetch a tumor-vs-normal RNA-seq matrix for a TCGA cancer type.

        Parameters
        ----------
        cancer_type
            TCGA project abbreviation, e.g. ``'BRCA'``, ``'LUAD'``, ``'COAD'``.
            A leading ``'TCGA-'`` is also accepted.
        n_tumor, n_normal
            Number of tumor / normal samples to download. The GDC API caps a
            single page at 500; values larger than that are truncated.
        workflow_type
            GDC RNA-seq workflow. ``'STAR - Counts'`` (current standard, has a
            ``gene_name`` column) or legacy ``'HTSeq - FPKM'`` /
            ``'HTSeq - Counts'`` (Ensembl IDs only).
        value_column
            Column to use as the expression value. If ``None``, a default is
            chosen for the workflow (FPKM for STAR-Counts, FPKM for HTSeq-FPKM,
            ``unstranded`` for HTSeq-Counts).
        gene_types
            Biotype filter for STAR - Counts rows (``gene_type`` column).
            Defaults to protein-coding only.
        max_genes
            Cap on the number of gene rows returned. Keeps the DE matrix small
            so downstream validation is fast — matches the GEO downloader.
        dry_run
            If ``True``, return synthetic-shaped data and perform **no** network
            I/O. Useful for offline tests and pipeline smoke-runs.
        random_state
            Seed for the synthetic dry-run generator.

        Returns
        -------
        (expression_matrix, gene_symbols, group_labels) or ``None`` on failure.

            expression_matrix : float np.ndarray, shape (n_genes, n_samples)
            gene_symbols      : List[str], length n_genes
            group_labels      : int np.ndarray, 0=normal, 1=tumor,
                                length n_tumor + n_normal
        """
        project_id = _normalize_project_id(cancer_type)
        value_col = value_column or _default_value_column(workflow_type)

        logger.info(
            "🌐 TCGAConnector: %s project=%s workflow=%r value=%r "
            "(n_tumor=%d, n_normal=%d, dry_run=%s)",
            "DRY-RUN" if dry_run else "GDC",
            project_id,
            workflow_type,
            value_col,
            n_tumor,
            n_normal,
            dry_run,
        )

        if dry_run:
            return self._dry_run_fetch(
                project_id=project_id,
                n_tumor=n_tumor,
                n_normal=n_normal,
                max_genes=max_genes,
                value_column=value_col,
                random_state=random_state,
            )

        # ---- 1. list RNA-seq file UUIDs for tumor and normal --------------
        try:
            tumor_files = self.list_files(
                project_id=project_id,
                workflow_type=workflow_type,
                sample_types=TUMOR_SAMPLE_TYPES,
                n=n_tumor,
            )
            normal_files = self.list_files(
                project_id=project_id,
                workflow_type=workflow_type,
                sample_types=NORMAL_SAMPLE_TYPES,
                n=n_normal,
            )
        except GDCAPIError as exc:
            logger.error("❌ GDC /files query failed for %s: %s", project_id, exc)
            return None

        if not tumor_files:
            logger.warning(
                "⚠️  No tumor RNA-seq files found for %s (workflow=%s)",
                project_id,
                workflow_type,
            )
            return None
        if not normal_files:
            logger.warning(
                "⚠️  No normal RNA-seq files found for %s (workflow=%s) — "
                "cannot build a tumor-vs-normal contrast",
                project_id,
                workflow_type,
            )
            return None

        tumor_ids = [h["file_id"] for h in tumor_files]
        normal_ids = [h["file_id"] for h in normal_files]
        logger.info(
            "   Found %d tumor + %d normal files (workflow=%s)",
            len(tumor_ids),
            len(normal_ids),
            workflow_type,
        )

        # ---- 2. download + parse each file --------------------------------
        # order: tumor columns first, then normal; labels follow the same order.
        ordered_ids: List[str] = list(tumor_ids) + list(normal_ids)
        parsed_per_sample: List[Tuple[str, Dict[str, float]]] = []
        for idx, file_id in enumerate(ordered_ids):
            label = "tumor" if idx < len(tumor_ids) else "normal"
            try:
                content = self.download_file(file_id)
            except GDCAPIError as exc:
                logger.warning(
                    "   Skipping %s file %s (%s): %s", label, file_id, project_id, exc
                )
                continue
            if content is None:
                continue
            symbols_values = self._parse_rnaseq_bytes(
                content,
                workflow_type=workflow_type,
                value_column=value_col,
                gene_types=tuple(gene_types),
            )
            if not symbols_values:
                logger.warning(
                    "   Could not parse file %s (%s); skipped", file_id, label
                )
                continue
            parsed_per_sample.append((label, symbols_values))

        n_tumor_parsed = sum(1 for lab, _ in parsed_per_sample if lab == "tumor")
        n_normal_parsed = sum(1 for lab, _ in parsed_per_sample if lab == "normal")
        if n_tumor_parsed == 0 or n_normal_parsed == 0:
            logger.error(
                "❌ Insufficient parsed samples for a contrast "
                "(tumor=%d, normal=%d) for %s",
                n_tumor_parsed,
                n_normal_parsed,
                project_id,
            )
            return None

        # ---- 3. assemble matrix -------------------------------------------
        # Reorder so tumor columns are first (parsing may have skipped some
        # files, breaking the original ordering).
        parsed_per_sample.sort(key=lambda lv: 0 if lv[0] == "tumor" else 1)
        labels = np.array(
            [1 if lab == "tumor" else 0 for lab, _ in parsed_per_sample],
            dtype=int,
        )

        expression_matrix, gene_symbols = self._assemble_matrix(
            parsed_per_sample=[sv for _, sv in parsed_per_sample],
            max_genes=max_genes,
        )

        logger.info(
            "✅ TCGA %s assembled: %d genes × %d samples (tumor=%d, normal=%d)",
            project_id,
            len(gene_symbols),
            expression_matrix.shape[1],
            int(labels.sum()),
            int((labels == 0).sum()),
        )
        return expression_matrix, gene_symbols, labels

    def list_files(
        self,
        project_id: str,
        workflow_type: str,
        sample_types: Sequence[str],
        n: int,
        timeout: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Query the GDC ``/files`` endpoint for RNA-seq file metadata.

        Returns a list of hit dicts, each containing at least ``file_id`` and
        a nested ``cases`` list (with ``samples[].sample_type``). Raises
        :class:`GDCAPIError` on unrecoverable API failure.
        """
        filters = self._build_filters(
            project_id=project_id,
            workflow_type=workflow_type,
            sample_types=tuple(sample_types),
        )
        body = {
            "filters": filters,
            "fields": ",".join(_FILE_FIELDS),
            "format": "JSON",
            "size": max(1, min(int(n), 500)),  # GDC page cap
            "from": 0,
        }
        logger.debug(
            "   POST /files project=%s workflow=%r sample_types=%s size=%d",
            project_id,
            workflow_type,
            sample_types,
            body["size"],
        )
        response = self._request_with_retry(
            "POST",
            self.files_endpoint,
            json=body,
            timeout=timeout or self.timeout,
        )
        if response is None:
            raise GDCAPIError(
                f"/files request failed after {self.max_retries} retries "
                f"(project={project_id})"
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise GDCAPIError(f"/files returned non-JSON response: {exc}") from exc

        hits = (payload.get("data") or {}).get("hits") or []
        # Flatten the nested sample_type out of cases.samples for convenience.
        for hit in hits:
            hit.setdefault("sample_type", self._extract_sample_type(hit))
        return hits

    def download_file(
        self, file_id: str, timeout: Optional[int] = None
    ) -> Optional[bytes]:
        """Download raw bytes for a single GDC file UUID via ``GET /data/{id}``.

        Uses an in-memory cache so repeated calls for the same ``file_id`` in a
        single process do not re-hit the network. Returns ``None`` on failure.
        """
        if file_id in self._cache:
            return self._cache[file_id]
        url = f"{self.data_endpoint}/{file_id}"
        response = self._request_with_retry(
            "GET", url, timeout=timeout or self.timeout, stream=True
        )
        if response is None:
            return None
        # Bound the streamed read so a stalled socket cannot hang the discovery
        # loop indefinitely (the per-chunk read timeout does not always fire on
        # half-open sockets — same lesson as the GEO matrix downloader).
        content = self._read_stream_bounded(
            response, max_seconds=max(60, self.timeout * 10), max_bytes=64 * 1024 * 1024
        )
        if content is None:
            return None
        self._cache[file_id] = content
        if self.sleep_between_downloads > 0:
            time.sleep(self.sleep_between_downloads)
        return content

    # ------------------------------------------------------------------
    # Internals — API plumbing
    # ------------------------------------------------------------------
    def _build_filters(
        self,
        project_id: str,
        workflow_type: str,
        sample_types: Tuple[str, ...],
    ) -> Dict[str, Any]:
        """Build the nested GDC filter object for the /files endpoint."""
        return {
            "op": "and",
            "content": [
                {
                    "op": "in",
                    "content": {
                        "field": "cases.project.project_id",
                        "value": [project_id],
                    },
                },
                {
                    "op": "in",
                    "content": {
                        "field": "data_category",
                        "value": ["Transcriptome Profiling"],
                    },
                },
                {
                    "op": "in",
                    "content": {
                        "field": "data_type",
                        "value": ["Gene Expression Quantification"],
                    },
                },
                {
                    "op": "in",
                    "content": {
                        "field": "experimental_strategy",
                        "value": ["RNA-Seq"],
                    },
                },
                {
                    "op": "in",
                    "content": {
                        "field": "analysis.workflow_type",
                        "value": [workflow_type],
                    },
                },
                {
                    "op": "in",
                    "content": {
                        "field": "cases.samples.sample_type",
                        "value": list(sample_types),
                    },
                },
                {"op": "=", "content": {"field": "access", "value": "open"}},
            ],
        }

    def _request_with_retry(
        self, method: str, url: str, **kwargs: Any
    ) -> Optional[requests.Response]:
        """Issue an HTTP request with exponential backoff on transient errors.

        Retries on timeouts, connection errors, 429 (rate limit), and 5xx.
        Returns the :class:`requests.Response` on success or ``None`` if every
        attempt fails.
        """
        last_err: Optional[BaseException] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method, url, headers=self.headers, **kwargs
                )
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_err = exc
                logger.debug(
                    "   %s %s network error (attempt %d/%d): %s",
                    method,
                    url,
                    attempt + 1,
                    self.max_retries + 1,
                    exc,
                )
            else:
                status = response.status_code
                if status == 200:
                    return response
                # Retryable: rate limit + transient server errors.
                if status in (429, 500, 502, 503, 504):
                    last_err = GDCAPIError(f"HTTP {status} from {url}")
                    logger.debug(
                        "   %s %s -> HTTP %d (attempt %d/%d)",
                        method,
                        url,
                        status,
                        attempt + 1,
                        self.max_retries + 1,
                    )
                    # Respect a Retry-After hint when present.
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and attempt < self.max_retries:
                        try:
                            time.sleep(min(float(retry_after), 60.0))
                            continue
                        except ValueError:
                            pass
                else:
                    # Non-retryable client error — log and stop.
                    logger.warning("   %s %s -> HTTP %d", method, url, status)
                    return response

            if attempt >= self.max_retries:
                break
            wait = self.backoff * (2 ** attempt)
            logger.debug("   backing off %.1fs before retry", wait)
            time.sleep(wait)

        if last_err is not None:
            logger.warning("   %s %s exhausted retries: %s", method, url, last_err)
        return None

    def _read_stream_bounded(
        self,
        response: requests.Response,
        max_seconds: int = 600,
        max_bytes: int = 64 * 1024 * 1024,
    ) -> Optional[bytes]:
        """Read a streamed response with hard total-time and total-size caps."""
        start = time.monotonic()
        chunks: List[bytes] = []
        total = 0
        try:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    logger.warning(
                        "   GDC file exceeds %d MB cap, aborting", max_bytes // (1024 * 1024)
                    )
                    return None
                if time.monotonic() - start > max_seconds:
                    logger.warning(
                        "   GDC download exceeded %ds deadline, aborting", max_seconds
                    )
                    return None
                chunks.append(chunk)
        except requests.exceptions.RequestException as exc:
            logger.warning("   GDC stream read failed: %s", exc)
            return None
        logger.debug(
            "   Streamed %d bytes in %.1fs", total, time.monotonic() - start
        )
        return b"".join(chunks)

    @staticmethod
    def _extract_sample_type(hit: Dict[str, Any]) -> str:
        """Pull the first sample_type out of a /files hit's nested cases."""
        for case in hit.get("cases") or []:
            for sample in case.get("samples") or []:
                st = sample.get("sample_type")
                if st:
                    return st if isinstance(st, str) else (st[0] if st else "")
        return ""

    # ------------------------------------------------------------------
    # Internals — file parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _maybe_gunzip(content: bytes) -> bytes:
        """Transparently decompress gzip if the magic header is present."""
        if len(content) >= 2 and content[0:2] == b"\x1f\x8b":
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(content)) as fh:
                    return fh.read()
            except OSError as exc:
                logger.debug("   gzip decompress failed (%s); using raw bytes", exc)
        return content

    @classmethod
    def _parse_rnaseq_bytes(
        cls,
        content: bytes,
        workflow_type: str,
        value_column: str,
        gene_types: Tuple[str, ...],
    ) -> Dict[str, float]:
        """Parse one GDC RNA-seq file into a ``{gene_symbol: value}`` dict.

        Duplicate symbols (multiple Ensembl IDs mapping to one HGNC symbol)
        are summed so the total signal for a gene is preserved.
        """
        raw = cls._maybe_gunzip(content)
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("   Could not decode RNA-seq file: %s", exc)
            return {}

        lines = text.splitlines()
        if not lines:
            return {}

        # Locate the header (first line containing 'gene_id').
        header_idx = -1
        header_cols: List[str] = []
        for i, line in enumerate(lines[:5]):
            cols = line.rstrip("\n").split("\t")
            if cols and cols[0].lower().startswith("gene_id"):
                header_idx = i
                header_cols = [c.strip().lower() for c in cols]
                break

        out: Dict[str, float] = {}

        if header_idx == -1:
            # No header — legacy HTSeq 2-column format (gene_id<TAB>value).
            # Infer the value column as the last numeric field.
            for line in lines:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 2:
                    continue
                gene_id = parts[0].strip()
                if not gene_id or gene_id in _HTSEQ_SUMMARY_IDS:
                    continue
                try:
                    val = float(parts[-1])
                except ValueError:
                    continue
                # Ensembl ID (strip version suffix) is the only symbol we have.
                symbol = gene_id.split(".")[0]
                out[symbol] = out.get(symbol, 0.0) + val
            return out

        # Header-driven parse (STAR - Counts or any multi-column file).
        col_index = {name: i for i, name in enumerate(header_cols)}
        if "gene_id" not in col_index:
            logger.warning("   RNA-seq header has no 'gene_id' column: %s", header_cols)
            return {}
        if value_column.lower() not in col_index:
            logger.warning(
                "   value column %r not in file header %s; falling back to last column",
                value_column,
                header_cols,
            )
            value_idx = len(header_cols) - 1
        else:
            value_idx = col_index[value_column.lower()]

        gene_name_idx = col_index.get("gene_name")
        gene_type_idx = col_index.get("gene_type")
        allowed_types = set(gene_types) if gene_types else None

        for line in lines[header_idx + 1 :]:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= value_idx:
                continue
            gene_id = parts[col_index["gene_id"]].strip()
            if not gene_id or gene_id in _HTSEQ_SUMMARY_IDS:
                continue

            # Biotype filter (STAR - Counts only).
            if allowed_types and gene_type_idx is not None:
                if gene_type_idx < len(parts):
                    gtype = parts[gene_type_idx].strip()
                    if gtype not in allowed_types:
                        continue

            # Value.
            try:
                val = float(parts[value_idx])
            except ValueError:
                continue

            # Symbol: prefer gene_name, else Ensembl ID (version stripped).
            if gene_name_idx is not None and gene_name_idx < len(parts):
                symbol = parts[gene_name_idx].strip()
            else:
                symbol = gene_id.split(".")[0]
            if not symbol:
                symbol = gene_id.split(".")[0]

            out[symbol] = out.get(symbol, 0.0) + val

        return out

    @staticmethod
    def _assemble_matrix(
        parsed_per_sample: List[Dict[str, float]],
        max_genes: int,
    ) -> Tuple[np.ndarray, List[str]]:
        """Align per-sample dicts into a (genes x samples) float matrix.

        Gene order is taken from the first sample (GDC files from the same
        workflow share a fixed GTF order). Genes missing in a later sample are
        filled with 0.0. Truncated to the first ``max_genes`` rows.
        """
        if not parsed_per_sample:
            return np.empty((0, 0), dtype=float), []

        # Canonical gene order from the first sample, capped at max_genes.
        canonical: List[str] = list(parsed_per_sample[0].keys())[:max_genes]
        n_genes = len(canonical)
        n_samples = len(parsed_per_sample)
        gene_pos = {sym: i for i, sym in enumerate(canonical)}

        matrix = np.zeros((n_genes, n_samples), dtype=float)
        for col, sample_dict in enumerate(parsed_per_sample):
            for sym, val in sample_dict.items():
                row = gene_pos.get(sym)
                if row is not None:
                    matrix[row, col] = val
        return matrix, canonical

    # ------------------------------------------------------------------
    # Internals — dry run (offline)
    # ------------------------------------------------------------------
    def _dry_run_fetch(
        self,
        project_id: str,
        n_tumor: int,
        n_normal: int,
        max_genes: int,
        value_column: str,
        random_state: int,
    ) -> Tuple[np.ndarray, List[str], np.ndarray]:
        """Return synthetic-shaped data with no network access.

        Generates a small, deterministic expression matrix with a real-looking
        built-in HGNC symbol set and a handful of genes with an injected
        tumor-vs-normal effect so the downstream DE analyzer produces
        non-trivial output during smoke tests.
        """
        rng = np.random.default_rng(random_state)
        n_samples = max(1, n_tumor) + max(1, n_normal)
        # A small real-symbol palette, cycled to reach max_genes.
        palette = [
            "TSPAN6", "DPM1", "SCYL3", "C1orf112", "FGR", "CFH", "FUCA2",
            "GCLC", "NFYA", "STPG1", "AOC1", "C1orf159", "MFAP2", "MIIP",
            "RPL22", "KDM1A", "PLA2G2A", "TMEM60", "ACTB", "GAPDH", "TP53",
            "BRCA1", "BRCA2", "EGFR", "MYC", "PTEN", "KRAS", "PIK3CA",
        ]
        n_genes = min(max_genes, 500)
        gene_symbols = [palette[i % len(palette)] for i in range(n_genes)]

        # FPKM-like: lognormal, mostly under a few hundred, occasionally higher.
        # The DE analyzer auto-applies log2(x+1) when max > 100 — mirror that
        # by keeping values on roughly FPKM scale.
        base = rng.lognormal(mean=3.0, sigma=1.2, size=(n_genes, n_samples))
        matrix = base.astype(float)

        # Inject a clear tumor up-regulation in ~5% of genes so smoke tests of
        # the DE pipeline get non-empty significant-gene sets.
        n_de = max(1, n_genes // 20)
        de_idx = rng.choice(n_genes, size=n_de, replace=False)
        tumor_cols = np.arange(max(1, n_tumor))  # tumor columns come first
        for g in de_idx:
            matrix[g, tumor_cols] *= float(rng.uniform(2.0, 5.0))

        labels = np.array(
            [1] * max(1, n_tumor) + [0] * max(1, n_normal), dtype=int
        )

        logger.info(
            "✅ DRY-RUN %s: %d genes × %d samples (tumor=%d, normal=%d); "
            "%d injected DE genes; value_column=%r",
            project_id,
            n_genes,
            n_samples,
            int(labels.sum()),
            int((labels == 0).sum()),
            n_de,
            value_column,
        )
        return matrix, gene_symbols, labels


# ---------------------------------------------------------------------------
# Factory + module-level convenience
# ---------------------------------------------------------------------------
def create_tcga_connector() -> TCGAConnector:
    """Factory function for a :class:`TCGAConnector` (BIODISC convention)."""
    return TCGAConnector()


def fetch_tcga_expression(
    cancer_type: str,
    n_tumor: int = 20,
    n_normal: int = 20,
    workflow_type: str = "STAR - Counts",
    value_column: Optional[str] = None,
    gene_types: Sequence[str] = _DEFAULT_GENE_TYPES,
    max_genes: int = 2000,
    dry_run: bool = False,
    random_state: int = 42,
) -> Optional[Tuple[np.ndarray, List[str], np.ndarray]]:
    """Module-level convenience wrapper around :meth:`TCGAConnector.fetch_expression`.

    See :class:`TCGAConnector` for parameter semantics. Returns
    ``(expression_matrix, gene_symbols, group_labels)`` or ``None`` on failure.

    Examples
    --------
    >>> # Offline smoke test (no network):
    >>> matrix, symbols, labels = fetch_tcga_expression("BRCA", dry_run=True)
    >>> matrix.shape[0] == len(symbols)
    True
    >>> set(np.unique(labels).tolist()) <= {0, 1}
    True
    """
    return create_tcga_connector().fetch_expression(
        cancer_type=cancer_type,
        n_tumor=n_tumor,
        n_normal=n_normal,
        workflow_type=workflow_type,
        value_column=value_column,
        gene_types=gene_types,
        max_genes=max_genes,
        dry_run=dry_run,
        random_state=random_state,
    )


__all__ = [
    "TCGAConnector",
    "GDCAPIError",
    "create_tcga_connector",
    "fetch_tcga_expression",
    "TUMOR_SAMPLE_TYPES",
    "NORMAL_SAMPLE_TYPES",
]
