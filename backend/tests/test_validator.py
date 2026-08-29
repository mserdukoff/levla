from app.services.gloss import attach_glosses
from app.services.morph import analyze_text, analyze_word
from app.services.validator import validate_tokens


def tokens(text: str):
    return attach_glosses(analyze_text(text), use_llm=False)


def test_morph_lemma_and_case():
    morph = analyze_word("книгу")
    assert morph.lemma == "книга"
    assert morph.case == "acc"


def test_morph_instrumental():
    morph = analyze_word("карандашом")
    assert morph.case == "ins"


def test_a1_nominative_present_passes():
    text = "Я студент. Это книга. Книга новая. Мама здесь."
    result = validate_tokens(tokens(text), "A1")
    assert result.passed, result.flags
    assert result.forbidden_tense_rate == 0
    assert result.forbidden_case_rate == 0


def test_a1_rejects_past_tense():
    text = "Я был студент. Это была книга. Мама читала."
    result = validate_tokens(tokens(text), "A1")
    assert result.forbidden_tense_rate > 0
    assert any("tense:past" in f for f in result.flags)
    assert not result.passed


def test_a1_rejects_accusative():
    text = "Я читаю книгу. Папа видит маму."
    result = validate_tokens(tokens(text), "A1")
    assert result.forbidden_case_rate > 0
    assert any("case:acc" in f for f in result.flags)


def test_a1_rejects_subordinate_esli():
    text = "Я студент, если папа дома."
    result = validate_tokens(tokens(text), "A1")
    assert any("conj:если" in f for f in result.flags)
    assert not result.passed


def test_a2_allows_accusative_dative_past():
    text = "Вчера я купил хлеб в магазине. Потом я дал хлеб маме."
    result = validate_tokens(tokens(text), "A2")
    assert not any("case:acc" in f for f in result.flags)
    assert not any("case:dat" in f for f in result.flags)
    assert not any("case:prep" in f for f in result.flags)
    assert result.forbidden_tense_rate == 0


def test_a2_rejects_instrumental():
    text = "Он пишет письмо карандашом. Она ест суп ложкой."
    result = validate_tokens(tokens(text), "A2")
    assert any("case:ins" in f for f in result.flags)
    assert not result.passed


def test_a2_rejects_participle():
    text = "Книга, прочитанная студентом, лежит на столе."
    result = validate_tokens(tokens(text), "A2")
    assert any(f.startswith("pos:PRTF") or f.startswith("pos:PRTS") for f in result.flags)
    assert not result.passed


def test_b1_allows_instrumental():
    text = "Он работает врачом. Мы говорим с другом."
    result = validate_tokens(tokens(text), "B1")
    assert not any("case:ins" in f for f in result.flags)


def test_b1_rejects_subjunctive_by():
    text = "Если бы я знал это, я бы пришёл раньше."
    result = validate_tokens(tokens(text), "B1")
    assert any("conj:бы" in f for f in result.flags)
    assert not result.passed


def test_b2_allows_participle_and_by():
    text = (
        "Книга, прочитанная студентом, лежит на столе. "
        "Если бы он знал, он бы пришёл."
    )
    result = validate_tokens(tokens(text), "B2")
    assert not any(f.startswith("pos:PRTF") for f in result.flags)
    assert not any("conj:бы" in f for f in result.flags)


def test_gloss_attached_for_core_lemma():
    toks = tokens("Я читаю книгу.")
    book = next(t for t in toks if t.lemma == "книга")
    assert book.gloss == "book"
    i = next(t for t in toks if t.lemma == "я")
    assert i.gloss == "I"
