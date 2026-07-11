"""P2.3 — LLM question generator + generic/template gate."""
from biodisc_core.fixed_pipeline.question_generator import (
    is_generic_question, parse_questions, QuestionGenerator, get_questions_via_llm,
)


def test_specific_question_with_gene_token_passes_gate():
    assert not is_generic_question(
        "How does BRCA1 mutation status affect response to PARP inhibitors in triple-negative breast cancer?"
    )
    assert not is_generic_question(
        "Does STAT3 activation differ between IL-6 treated and untreated glioblastoma cells?"
    )


def test_generic_questions_are_rejected():
    assert is_generic_question("How does gene expression change in cancer cells?")
    assert is_generic_question("What genes are important?")
    assert is_generic_question("patient stratification")  # too short + saturated


def test_parse_strips_numbering_and_bullets():
    raw = "1. Does X inhibit Y?\n- How does Z work?\n2) Is W expressed?\n"
    qs = parse_questions(raw)
    assert qs == ["Does X inhibit Y?", "How does Z work?", "Is W expressed?"]


def test_generator_gates_a_mixed_batch():
    raw = (
        "How does gene expression change in cancer?\n"                     # generic
        "Does BRCA1 loss alter RAD51 foci formation after irradiation?\n"  # specific
        "1. What genes matter?\n"                                          # generic
    )
    proposer = lambda system, user: raw  # noqa: E731
    gen = QuestionGenerator(proposer)
    results = gen.generate()
    texts = {g.text: g.rejected for g in results}
    assert texts["Does BRCA1 loss alter RAD51 foci formation after irradiation?"] is False
    assert texts["How does gene expression change in cancer?"] is True


def test_get_questions_via_llm_returns_only_accepted():
    raw = (
        "How does gene expression change in cancer?\n"
        "Does AMPK activation alter glycolytic flux under glucose deprivation?\n"
    )
    proposer = lambda system, user: raw  # noqa: E731
    accepted = get_questions_via_llm(proposer, n=2)
    assert accepted == ["Does AMPK activation alter glycolytic flux under glucose deprivation?"]
