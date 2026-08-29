from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db import Base
from app.services.generate import ensure_translation, get_passage, save_authored_passage
from app.services.seed import SEED
from app.services.seed_translations import TRANSLATIONS


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_translations_cover_every_seed():
    missing = [
        (item["language"], item["title"])
        for item in SEED
        if (item["language"], item["title"]) not in TRANSLATIONS
    ]
    assert missing == []
    empty = [k for k, v in TRANSLATIONS.items() if not v.strip()]
    assert empty == []


def test_save_authored_passage_stores_translation():
    db = _session()
    item = SEED[0]
    english = TRANSLATIONS[(item["language"], item["title"])]
    row = save_authored_passage(
        db,
        language=item["language"],
        level=item["level"],
        topic=item["topic"],
        genre=item.get("genre"),
        title=item["title"],
        text=item["text"],
        translation=english,
    )
    passage = get_passage(db, row.id)
    assert passage is not None
    assert passage.translation == english
    assert ensure_translation(db, row.id) == english
