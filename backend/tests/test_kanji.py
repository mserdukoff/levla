from app.services.kanji import breakdown
from app.services.morph import analyze_text


def _by_text(text: str, surface: str):
    toks = analyze_text(text, "ja")
    return next(t for t in toks if t.text == surface)


def test_shijou_aligns_readings_and_meanings():
    parts = breakdown("市場", "しじょう")
    assert [p.char for p in parts] == ["市", "場"]
    assert parts[0].reading == "し"
    assert parts[1].reading == "じょう"
    assert "city" in parts[0].meaning or "market" in parts[0].meaning
    assert "place" in parts[1].meaning or "location" in parts[1].meaning


def test_gakusei_compound():
    parts = breakdown("学生", "がくせい")
    assert parts[0].char == "学" and parts[0].reading == "がく"
    assert parts[1].char == "生" and parts[1].reading == "せい"
    assert parts[0].meaning
    assert parts[1].meaning


def test_taberu_okurigana():
    parts = breakdown("食べる", "たべる")
    assert len(parts) == 1
    assert parts[0].char == "食"
    assert parts[0].reading == "た"
    assert "eat" in parts[0].meaning


def test_hon_single_kanji():
    parts = breakdown("本", "ほん")
    assert len(parts) == 1
    assert parts[0].reading == "ほん"
    assert parts[0].meaning


def test_tokens_include_kanji_breakdown():
    tok = _by_text("市場の朝", "市場")
    assert tok.kanji
    assert tok.kanji[0].char == "市"
    assert tok.kanji[0].reading == "し"
    assert tok.kanji[1].char == "場"
    assert tok.kanji[1].reading == "じょう"


def test_kana_only_has_no_kanji_parts():
    tok = _by_text("これは本です。", "これ")
    assert tok.kanji == []


def test_hon_dictionary_details():
    parts = breakdown("本", "ほん")
    p = parts[0]
    assert p.on == ["ホン"]
    assert "もと" in p.kun
    assert p.strokes == 5
    assert p.jlpt == 5
    assert p.grade == 1
    assert p.freq == 10
    assert p.radical == "木"
    assert p.radical_name == "tree"
    assert "一" in p.parts and "木" in p.parts
    assert "book" in p.meaning
    assert "origin" in p.meaning


def test_go_on_kun_and_jlpt():
    parts = breakdown("語", "ご")
    p = parts[0]
    assert p.reading == "ご"
    assert p.on == ["ゴ"]
    assert "かた.る" in p.kun
    assert p.strokes == 14
    assert p.jlpt == 5
    assert p.grade == 2
    assert p.radical == "言"
    assert p.radical_name == "speech"
    assert "口" in p.parts and "言" in p.parts


def test_taberu_keeps_okurigana_on_kun():
    parts = breakdown("食べる", "たべる")
    assert parts[0].reading == "た"
    assert "た.べる" in parts[0].kun
    assert "ショク" in parts[0].on
