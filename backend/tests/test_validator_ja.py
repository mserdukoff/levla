from app.services.gloss import attach_glosses
from app.services.morph import analyze_text, analyze_word
from app.services.validator import validate_tokens


def ja_tokens(text: str):
    return attach_glosses(analyze_text(text, "ja"), use_llm=False, language="ja")


def test_ja_lemma_and_reading():
    morph = analyze_word("本", "ja")
    assert morph.lemma == "本"
    assert morph.pos == "noun"
    assert morph.reading in {"ほん", "もと", None} or (
        morph.reading is not None and "ほ" in morph.reading
    )


def test_ja_a1_desu_masu_passes():
    text = "私は学生です。これは本です。本は新しいです。"
    result = validate_tokens(ja_tokens(text), "A1", "ja")
    assert result.passed, result.flags


def test_ja_a1_rejects_te_form():
    text = "本を読んでください。"
    result = validate_tokens(ja_tokens(text), "A1", "ja")
    assert any("ja:te_form" in f for f in result.flags)
    assert not result.passed


def test_ja_a2_allows_te_form():
    text = "本を読んでください。それから水を飲みます。"
    result = validate_tokens(ja_tokens(text), "A2", "ja")
    assert not any("ja:te_form" in f for f in result.flags)


def test_ja_a2_rejects_te_iru():
    text = "今、本を読んでいます。"
    result = validate_tokens(ja_tokens(text), "A2", "ja")
    assert any("ja:te_iru" in f for f in result.flags)
    assert not result.passed


def test_ja_b1_allows_te_iru():
    text = "今、本を読んでいます。"
    result = validate_tokens(ja_tokens(text), "B1", "ja")
    assert not any("ja:te_iru" in f for f in result.flags)


def test_ja_b1_rejects_keigo():
    text = "先生がいらっしゃいます。"
    result = validate_tokens(ja_tokens(text), "B1", "ja")
    assert any("ja:keigo" in f for f in result.flags)
    assert not result.passed


def test_ja_b2_allows_keigo():
    text = "先生がいらっしゃいます。"
    result = validate_tokens(ja_tokens(text), "B2", "ja")
    assert not any("ja:keigo" in f for f in result.flags)


def test_ja_gloss_core_lemma():
    toks = ja_tokens("私は学生です。")
    watashi = next(t for t in toks if t.lemma == "私")
    assert watashi.gloss == "I"
