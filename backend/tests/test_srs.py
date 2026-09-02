from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db import Base
from app.services.generate import save_authored_passage
from app.services.identity import Identity
from app.services.learner import star_lemma
from app.services.srs import due_cards, review_card


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_star_creates_due_card_and_sm2_advances():
    db = _session()
    passage = save_authored_passage(
        db,
        language="ja",
        level="A1",
        topic="table",
        genre="daily_life",
        title="これは本です",
        text="これは本です。本は新しいです。",
    )
    ident = Identity(user_id=None, device_id="test-srs-1")
    star_lemma(db, ident, "ja", "本", "book", passage.id)
    cards = due_cards(db, ident, "ja")
    assert len(cards) == 1
    assert cards[0].lemma == "本"
    updated = review_card(db, ident, cards[0].id, "good")
    assert updated.due_at > cards[0].due_at
    assert due_cards(db, ident, "ja") == []
