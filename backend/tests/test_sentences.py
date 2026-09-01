from app.services.morph import analyze_text


def _sentence_ids(tokens, language: str) -> list[int]:
    ja_end = set("。！？")
    ru_end = set(".!?…")
    end = ja_end if language == "ja" else ru_end
    ids: list[int] = []
    sid = 0
    for tok in tokens:
        ids.append(sid)
        if not tok.is_word and any(ch in end for ch in tok.text):
            sid += 1
    return ids


def test_japanese_sentence_index_advances_on_period():
    toks = analyze_text("今日は駅に行きます。駅は家の近くです。", "ja")
    ids = _sentence_ids(toks, "ja")
    kyou = next(i for i, t in enumerate(toks) if t.text == "今日")
    chikaku = next(i for i, t in enumerate(toks) if t.text == "近く")
    assert ids[kyou] == 0
    assert ids[chikaku] == 1


def test_english_split_matches_seed_style():
    text = (
        "Today I go to the station. The station is near the house. I take the train."
    )
    import re

    parts = [s.strip() for s in re.split(r"(?<=[.!?])(?:\s+|$)", text) if s.strip()]
    assert len(parts) == 3
    assert parts[0].startswith("Today")
    assert parts[1].startswith("The station")
