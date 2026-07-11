"""Apply LLM-proposed search-and-replace diffs to program source (AlphaEvolve).

Diff format (one or more blocks):

    <<< SEARCH
    exact original code to find
    ===
    replacement code
    >>> REPLACE

Parsing is a strict state machine; malformed diffs raise ValueError and the
caller rejects the candidate (AlphaEvolve trusts the evaluator, not the LLM).
A full-program fallback is also supported for short rewrites.
"""
import re
from dataclasses import dataclass
from typing import List

_SEARCH_START = "<<< SEARCH"
_SEPARATOR = "==="
_REPLACE_END = ">>> REPLACE"


@dataclass
class DiffBlock:
    search: str
    replace: str


class DiffParseError(ValueError):
    """Raised when diff text is malformed."""


def parse_diffs(text: str) -> List[DiffBlock]:
    """Parse diff text into a list of DiffBlock. Raises DiffParseError if malformed."""
    if not text:
        raise DiffParseError("empty diff text")

    lines = text.splitlines()
    blocks: List[DiffBlock] = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == _SEARCH_START:
            # Collect search lines until the '===' separator.
            search_lines: List[str] = []
            i += 1
            while i < n and lines[i].strip() != _SEPARATOR:
                search_lines.append(lines[i])
                i += 1
            if i >= n:
                raise DiffParseError("diff block missing '===' separator")
            # Collect replace lines until '>>> REPLACE'.
            replace_lines: List[str] = []
            i += 1  # skip separator
            while i < n and lines[i].strip() != _REPLACE_END:
                replace_lines.append(lines[i])
                i += 1
            if i >= n:
                raise DiffParseError("diff block missing '>>> REPLACE' terminator")
            i += 1  # skip terminator
            search = "\n".join(search_lines).strip("\n")
            replace = "\n".join(replace_lines).strip("\n")
            if not search:
                raise DiffParseError("diff block has empty SEARCH segment")
            blocks.append(DiffBlock(search=search, replace=replace))
        else:
            i += 1

    if not blocks:
        raise DiffParseError("no diff blocks found")
    return blocks


class DiffApplyError(ValueError):
    """Raised when a SEARCH segment is not present in the source."""


def apply_diffs(source: str, diffs: List[DiffBlock]) -> str:
    """Apply diff blocks in order. Raises DiffApplyError if any SEARCH is absent."""
    current = source
    for idx, d in enumerate(diffs):
        if d.search not in current:
            raise DiffApplyError(
                f"SEARCH segment #{idx + 1} not found in source (must match exactly)"
            )
        current = current.replace(d.search, d.replace, 1)
    return current


_FULL_PROGRAM_RE = re.compile(r"^\s*def\s+score\s*\(", re.MULTILINE)


def apply_diffs_or_full(source: str, text: str) -> str:
    """Apply parsed diffs; fall back to using ``text`` verbatim if it is a full
    program (contains ``def score(``). Raises if neither applies.

    This mirrors AlphaEvolve: short edits use diffs, full rewrites emit the
    entire code block.
    """
    try:
        diffs = parse_diffs(text)
        return apply_diffs(source, diffs)
    except DiffParseError:
        # Maybe the model emitted a full program instead of diffs.
        stripped = text.strip().strip("`")
        # Strip a leading language fence line like ```python if present.
        if stripped.startswith("python\n"):
            stripped = stripped[len("python\n"):]
        if _FULL_PROGRAM_RE.search(stripped) and validate_score_program(stripped):
            return stripped
        raise DiffParseError(
            "text is neither valid diff blocks nor a full program defining `score`"
        )


def validate_score_program(source: str) -> bool:
    """True if source parses and defines a top-level ``score`` function."""
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(node, ast.FunctionDef) and node.name == "score"
        for node in tree.body
    )
