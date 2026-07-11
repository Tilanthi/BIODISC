"""P1.2 — diff_applier: parse + apply AlphaEvolve search/replace diffs."""
import pytest

from biodisc_core.evolution.diff_applier import (
    parse_diffs, apply_diffs, apply_diffs_or_full, DiffParseError, DiffApplyError,
)

SOURCE = "def score(x):\n    return x + 1\n"


def test_parse_single_block():
    diff = "<<< SEARCH\nreturn x + 1\n===\nreturn x + 2\n>>> REPLACE\n"
    blocks = parse_diffs(diff)
    assert len(blocks) == 1
    assert blocks[0].search == "return x + 1"
    assert blocks[0].replace == "return x + 2"


def test_parse_multiple_blocks():
    diff = (
        "<<< SEARCH\na\n===\nA\n>>> REPLACE\n"
        "<<< SEARCH\nb\n===\nB\n>>> REPLACE\n"
    )
    blocks = parse_diffs(diff)
    assert [b.search for b in blocks] == ["a", "b"]
    assert [b.replace for b in blocks] == ["A", "B"]


def test_malformed_missing_terminator_raises():
    with pytest.raises(DiffParseError):
        parse_diffs("<<< SEARCH\nx\n===\ny\n")  # no >>> REPLACE


def test_malformed_empty_search_raises():
    with pytest.raises(DiffParseError):
        parse_diffs("<<< SEARCH\n===\ny\n>>> REPLACE\n")


def test_apply_diff_replaces_exact_segment():
    blocks = parse_diffs("<<< SEARCH\nreturn x + 1\n===\nreturn x + 2\n>>> REPLACE\n")
    out = apply_diffs(SOURCE, blocks)
    assert "return x + 2" in out
    assert "return x + 1" not in out


def test_apply_diff_search_not_found_raises():
    blocks = parse_diffs("<<< SEARCH\nNONEXISTENT\n===\nwhatever\n>>> REPLACE\n")
    with pytest.raises(DiffApplyError):
        apply_diffs(SOURCE, blocks)


def test_full_program_fallback():
    full = "def score(expression, labels):\n    return expression[0]\n"
    # No diff markers -> should be accepted as a full program replacement.
    out = apply_diffs_or_full(SOURCE, full)
    assert "return expression[0]" in out


def test_neither_diff_nor_program_raises():
    with pytest.raises(DiffParseError):
        apply_diffs_or_full(SOURCE, "this is just prose, not code or diffs")
