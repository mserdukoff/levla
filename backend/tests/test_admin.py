from app.core.config import Settings
from app.models.db import Base, UserRow
from app.services.admin import admin_overview, is_admin_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_admin_email_set_is_case_insensitive():
    s = Settings.model_construct(admin_emails="You@Example.com, other@x.com")
    assert s.admin_email_set == {"you@example.com", "other@x.com"}
    assert s.is_admin_email("you@example.com")
    assert s.is_admin_email("YOU@example.com")
    assert not s.is_admin_email("stranger@x.com")
    assert not s.is_admin_email(None)


def test_empty_admin_list_admits_nobody():
    s = Settings.model_construct(admin_emails="")
    assert s.admin_email_set == set()
    assert not s.is_admin_email("you@example.com")


def test_admin_overview_counts_users(monkeypatch):
    from app.core import config

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(UserRow(email="you@example.com", display_name="You"))
    db.add(UserRow(email="reader@example.com"))
    db.commit()
    monkeypatch.setattr(config.settings, "admin_emails", "you@example.com")
    overview = admin_overview(db)
    assert overview.totals["users"] == 2
    assert overview.api["name"] == "lociros"
    assert {u.email for u in overview.recent_users} == {"you@example.com", "reader@example.com"}
    assert is_admin_user(db.query(UserRow).filter_by(email="you@example.com").one())
    assert not is_admin_user(db.query(UserRow).filter_by(email="reader@example.com").one())
