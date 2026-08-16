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
"""GPL platform probe -> gene-symbol mapping (the real-data unlock).

Most real microarray matrices (Affymetrix `_at`, Illumina `ILMN_`) use probe IDs,
which the gene-symbol gate (P0.1) correctly rejects — publishing "ILMN_1343291 is
upregulated" is biologically meaningless. The correct fix is to map probes to
gene symbols via the GEO GPL platform annotation, then analyse on real symbols.

SAFETY: a buggy mapper that mis-maps probes would create WRONG gene symbols —
worse than rejecting. So this module is conservative: it only maps when it can
fetch the platform annotation and parse an explicit `Gene symbol` column, it
caches the mapping to disk, and callers must require a minimum mapping rate and
fall back to REJECTING (never fabricating) when mapping is unavailable or poor.
"""
import gzip
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "cache", "gpl"
)

# Minimum fraction of probes that must map to accept the dataset.
MIN_MAPPING_RATE = 0.5


def detect_probe_platform(gene_ids: List[str]) -> Optional[str]:
    """Return 'illumina' or 'affy' if probe IDs dominate, else None."""
    sample = " ".join(gene_ids[:300])
    if re.search(r"\bILMN_\d+\b", sample):
        return "illumina"
    if re.search(r"_at\b", sample):
        return "affy"
    return None


def extract_platform_id(matrix_text: str) -> Optional[str]:
    """GPL id (e.g. GPL570) from series-matrix metadata, or None.

    Handles both SOFT (``!Series_platform_id = GPL570``) and series-matrix
    (``!Series_platform_id\\t"GPL570"``) formats.
    """
    m = re.search(r"!Series_platform_id[\s=]+\"?(GPL\d+)", matrix_text)
    if m:
        return m.group(1)
    m = re.search(r"!Sample_platform_id[\s=]+\"?(GPL\d+)", matrix_text)
    return m.group(1) if m else None


def _parse_gpl_table(text: str) -> Dict[str, str]:
    """Parse a GPL annot/soft file into {probe_id: gene_symbol}.

    Requires an explicit column header with an ID column and a 'Gene symbol'
    (or 'IDENTIFIER') column. Returns {} if it can't find both (refuses to guess).
    """
    lines = text.split("\n")
    begin = -1
    for i, line in enumerate(lines):
        if "!platform_table_begin" in line.lower():
            begin = i + 1
            break
    if begin < 0 or begin >= len(lines):
        return {}

    cols = [c.strip().strip('"') for c in lines[begin].split("\t")]
    id_col = gs_col = -1
    for j, c in enumerate(cols):
        cl = c.lower()
        if cl in ("id", "probe_id", "probe set id"):
            id_col = j
        if cl in ("gene symbol", "gene_symbol", "symbol", "identifier", "gene_symbol"):
            gs_col = j
    if id_col < 0 or gs_col < 0:
        return {}

    mapping: Dict[str, str] = {}
    for line in lines[begin + 1:]:
        if "!platform_table_end" in line.lower():
            break
        parts = line.split("\t")
        if len(parts) <= max(id_col, gs_col):
            continue
        pid = parts[id_col].strip().strip('"')
        sym = parts[gs_col].strip().strip('"')
        if pid and sym and sym not in ("", "---", "."):
            # GPL entries may list multiple symbols; keep the first.
            mapping[pid] = sym.split(",")[0].strip()
    return mapping


def load_gpl_symbol_map(
    platform_id: str, cache_dir: str = CACHE_DIR, timeout: int = 90
) -> Dict[str, str]:
    """Fetch + parse a GPL annotation (cached). Returns {} on any failure."""
    cache_path = os.path.join(cache_dir, f"{platform_id}.tsv")
    if os.path.exists(cache_path):
        mapping: Dict[str, str] = {}
        with open(cache_path) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) == 2 and p[1]:
                    mapping[p[0]] = p[1]
        if mapping:
            return mapping

    prefix = platform_id[:5]  # e.g. GPL57 -> GPLnnn grouping uses first digits
    # GEO groups platforms as GPL{n}nnn. Build the directory from the numeric part.
    num = re.search(r"GPL(\d+)", platform_id)
    if not num:
        return {}
    n = num.group(1)
    group = f"GPL{n[:-3] or '0'}nnn" if len(n) > 3 else "GPLnnn"
    candidates = [
        f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{group}/{platform_id}/annot/{platform_id}.annot.gz",
        f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{group}/{platform_id}/soft/{platform_id}.family.soft.gz",
    ]
    for url in candidates:
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code != 200 or not r.content:
                continue
            try:
                text = gzip.decompress(r.content).decode("utf-8", "ignore")
            except Exception:
                text = r.content.decode("utf-8", "ignore")
            mapping = _parse_gpl_table(text)
            if mapping:
                os.makedirs(cache_dir, exist_ok=True)
                with open(cache_path, "w") as f:
                    for k, v in mapping.items():
                        f.write(f"{k}\t{v}\n")
                logger.info(f"   GPL {platform_id}: loaded {len(mapping)} probe->symbol mappings (cached)")
                return mapping
        except Exception as e:
            logger.info(f"   GPL fetch failed for {url}: {e}")
    return {}


def map_probes(gene_ids: List[str], mapping: Dict[str, str]) -> Tuple[List[str], List[int]]:
    """Return (symbols, kept_indices) for gene_ids that map to a symbol.

    GPL annotations join multiple symbols with '///' (and sometimes ','); the
    gene-symbol validator rejects such composite strings, so keep only the first
    token. Applied here so cached mappings are cleaned too.
    """
    symbols: List[str] = []
    kept: List[int] = []
    for i, gid in enumerate(gene_ids):
        sym = mapping.get(gid)
        if sym:
            sym = sym.split("///")[0].split(",")[0].strip()
            if sym and sym not in ("---", "."):
                symbols.append(sym)
                kept.append(i)
    return symbols, kept
