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
