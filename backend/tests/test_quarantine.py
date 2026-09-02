import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db import SHELF_PUBLIC, SHELF_QUARANTINE, Base, PassageRow
from app.services.generate import _persist, get_passage, save_authored_passage
from app.services.learner import pick_next_id
from app.services.library import list_library
from app.models.schemas import Calibration


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _failed_cal() -> Calibration:
    return Calibration(
        passed=False,
        attempts=2,
        overlevel_lemma_rate=0.4,
        subordinate_rate=0,
        forbidden_case_rate=0,
        forbidden_tense_rate=0,
        forbidden_pos_rate=0,
        flags=["ja:te_iru (いる)"],
        warnings=[],
    )


def test_failed_draft_is_quarantined_and_hidden():
    db = _session()
    from app.services.morph import analyze_text

    tokens = analyze_text("私は学生です。", "ja")
    row = _persist(
        db,
        language="ja",
        level="A1",
        topic="fail",
        genre="daily_life",
        title="失敗",
        text="私は学生です。",
        tokens=tokens,
        calibration=_failed_cal(),
    )
    assert row.shelf_status == SHELF_QUARANTINE
    assert get_passage(db, row.id) is None
    assert get_passage(db, row.id, include_quarantine=True) is not None
    library = list_library(db, "ja", "test-device-q")
    assert library.items == []
    assert pick_next_id(db, "ja", "A1", set()) is None


def test_passed_authored_text_is_public():
    db = _session()
    row = save_authored_passage(
        db,
        language="ja",
        level="A1",
        topic="home",
        genre="daily_life",
        title="私の朝",
        text="私は学生です。これは本です。本は新しいです。",
    )
    assert row.shelf_status == SHELF_PUBLIC or json.loads(row.calibration_json)["passed"]
    library = list_library(db, "ja", None)
    if json.loads(row.calibration_json)["passed"]:
        assert any(item.id == row.id for item in library.items)
        public = get_passage(db, row.id)
        assert public is not None
        assert public.calibration.allowed_constructions
        assert public.calibration.banned_constructions
