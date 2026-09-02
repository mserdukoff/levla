from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db import Base, LearnerReadRow
from app.services.identity import Identity
from app.services.trial import record_event, trial_metrics


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_trial_metrics_counts_second_reads_and_wtp():
    db = _session()
    ident = Identity(user_id=None, device_id="trial-device-1")
    now = datetime.now(timezone.utc)
    db.add(LearnerReadRow(device_id=ident.device_id, passage_id="p1", created_at=now))
    db.add(LearnerReadRow(device_id=ident.device_id, passage_id="p2", created_at=now))
    db.commit()
    record_event(db, kind="wtp", identity=ident)
    metrics = trial_metrics(db, days=30)
    assert metrics["learners_with_reads"] == 1
    assert metrics["second_text_completion"] == 1.0
    assert metrics["second_text_pass"] is True
    assert metrics["unsolicited_wtp"] >= 1
