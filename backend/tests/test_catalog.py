from app.services.catalog_ja import catalog_items
from app.services.passport import ALL_JA_CONSTRUCTIONS, construction_label
from app.services.sentences import english_aligned


def test_catalog_has_at_least_150_japanese_texts():
    items = catalog_items()
    assert len(items) >= 150
    assert all(item["language"] == "ja" for item in items)
    levels = {item["level"] for item in items}
    assert levels >= {"A1", "A2", "B1", "B2"}
    series = [i for i in items if i.get("series_id")]
    assert len(series) >= 8


def test_construction_labels_cover_ruleset():
    for key in ALL_JA_CONSTRUCTIONS:
        assert construction_label(key)


def test_catalog_english_matches_sentence_count():
    mismatches = [
        item["title"]
        for item in catalog_items()
        if not english_aligned(item["text"], item.get("translation"), "ja")
    ]
    assert mismatches == []
