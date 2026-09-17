from app.models.schemas import MorphInfo, Token
from app.services.validator import validate_tokens


def _tok(text: str, lemma: str, pos: str, **kwargs) -> Token:
    morph = MorphInfo(lemma=lemma, pos=pos, **kwargs)
    return Token(text=text, lemma=lemma, morph=morph, is_word=True)


def test_ar_a1_present_passes():
    tokens = [
        _tok("هذا", "هذا", "PRON"),
        _tok("بيت", "بيت", "NOUN", case="nom", state="indef"),
        Token(text=".", ws=" ", is_word=False),
        _tok("البيت", "بيت", "NOUN", case="nom", state="def"),
        _tok("كبير", "كبير", "ADJ"),
        Token(text=".", ws="", is_word=False),
    ]
    result = validate_tokens(tokens, "A1", "ar")
    assert result.passed, result.flags


def test_ar_a1_rejects_past():
    tokens = [
        _tok("ذهب", "ذهب", "VERB", tense="past", form="I", mood="indc"),
        _tok("إلى", "إلى", "ADP"),
        _tok("البيت", "بيت", "NOUN"),
        Token(text=".", ws="", is_word=False),
    ]
    result = validate_tokens(tokens, "A1", "ar")
    assert any("ar:perfect" in f or "tense:past" in f for f in result.flags)
    assert not result.passed


def test_ar_a1_rejects_form_ii():
    tokens = [
        _tok("درّس", "درس", "VERB", tense="pres", form="II", mood="indc"),
        _tok("في", "في", "ADP"),
        _tok("المدرسة", "مدرسة", "NOUN"),
        Token(text=".", ws="", is_word=False),
    ]
    result = validate_tokens(tokens, "A1", "ar")
    assert any("ar:form_ii" in f or "ar:derived_form" in f for f in result.flags)
    assert not result.passed


def test_ar_a2_allows_past_rejects_inna():
    past = [
        _tok("ذهب", "ذهب", "VERB", tense="past", form="I", mood="indc"),
        _tok("إلى", "إلى", "ADP"),
        _tok("السوق", "سوق", "NOUN"),
        Token(text=".", ws="", is_word=False),
    ]
    ok = validate_tokens(past, "A2", "ar")
    assert not any("ar:perfect" in f for f in ok.flags)

    inna = [
        _tok("إن", "إن", "PART"),
        _tok("البيت", "بيت", "NOUN"),
        _tok("كبير", "كبير", "ADJ"),
        Token(text=".", ws="", is_word=False),
    ]
    bad = validate_tokens(inna, "A2", "ar")
    assert any("ar:inna" in f for f in bad.flags)
    assert not bad.passed


def test_ar_b1_allows_inna_rejects_passive():
    inna = [
        _tok("إن", "إن", "PART"),
        _tok("البيت", "بيت", "NOUN"),
        _tok("كبير", "كبير", "ADJ"),
        Token(text=".", ws="", is_word=False),
    ]
    ok = validate_tokens(inna, "B1", "ar")
    assert not any("ar:inna" in f for f in ok.flags)

    passive = [
        _tok("كُتب", "كتب", "VERB", tense="past", form="I", voice="pass", mood="indc"),
        _tok("الكتاب", "كتاب", "NOUN"),
        Token(text=".", ws="", is_word=False),
    ]
    bad = validate_tokens(passive, "B1", "ar")
    assert any("ar:passive" in f for f in bad.flags)
    assert not bad.passed


def test_ar_b2_allows_passive():
    tokens = [
        _tok("كُتب", "كتب", "VERB", tense="past", form="I", voice="pass", mood="indc"),
        _tok("الكتاب", "كتاب", "NOUN"),
        Token(text=".", ws="", is_word=False),
    ]
    result = validate_tokens(tokens, "B2", "ar")
    assert not any("ar:passive" in f for f in result.flags)
