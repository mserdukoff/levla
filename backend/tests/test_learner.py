from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db import Base
from app.services.generate import complete_read, save_authored_passage
from app.services.learner import bump_level, lemma_token_stats, pick_next_id
from app.services.library import list_library
from app.services.morph import analyze_text


def test_bump_level_moves_one_step():
    assert bump_level("A2", "too_easy") == "B1"
    assert bump_level("A2", "too_hard") == "A1"
    assert bump_level("A1", "too_hard") == "A1"
    assert bump_level("B2", "too_easy") == "B2"


def test_lemma_token_stats_counts_occurrences():
    tokens = analyze_text("これは本です。本は新しいです。", "ja")
    new, recycled = lemma_token_stats(tokens, "ja", set())
    assert new > 0
    assert recycled == 0
    seen = {"本"}
    new2, recycled2 = lemma_token_stats(tokens, "ja", seen)
    assert recycled2 >= 2
    assert new2 == new - recycled2


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_too_easy_raises_placement_and_picks_next():
    db = _session()
    first = save_authored_passage(
        db,
        language="ja",
        level="A2",
        topic="home",
        genre="daily_life",
        title="私の朝",
        text="私は学生です。これは本です。本は新しいです。",
    )
    second = save_authored_passage(
        db,
        language="ja",
        level="B1",
        topic="reading",
        genre="daily_life",
        title="電車で本を読む",
        text="今、本を読んでいます。友達は駅にいます。",
    )
    result = complete_read(db, first.id, "too_easy", "test-device-1")
    assert result is not None
    assert result["placement"] == "B1"
    assert result["next_id"] == second.id
    assert result["new_lemmas"] > 0
    assert result["recycled_lemmas"] == 0

    library = list_library(db, "ja", "test-device-1")
    assert library.placement == "B1"
    assert library.next_id == second.id
    read = next(item for item in library.items if item.id == first.id)
    unread = next(item for item in library.items if item.id == second.id)
    assert read.read
    assert not unread.read
    assert unread.recycled_lemmas >= 1


def test_pick_next_skips_read_at_same_level():
    db = _session()
    a = save_authored_passage(
        db,
        language="ja",
        level="A2",
        topic="a",
        genre="daily_life",
        title="A",
        text="私は学生です。これは本です。",
    )
    b = save_authored_passage(
        db,
        language="ja",
        level="A2",
        topic="b",
        genre="daily_life",
        title="B",
        text="母は家にいます。水を飲みます。",
    )
    complete_read(db, a.id, "too_hard", "test-device-2")
    nxt = pick_next_id(db, "ja", "A1", {a.id}, exclude_id=a.id)
    assert nxt == b.id
