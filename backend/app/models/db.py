from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, UniqueConstraint, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


class PassageRow(Base):
    __tablename__ = "passages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), default="ru", index=True)
    level: Mapped[str] = mapped_column(String(8), index=True)
    topic: Mapped[str] = mapped_column(String(200))
    genre: Mapped[str | None] = mapped_column(String(40), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    text: Mapped[str] = mapped_column(Text)
    tokens_json: Mapped[str] = mapped_column(Text)
    calibration_json: Mapped[str] = mapped_column(Text)
    word_count: Mapped[int]
    translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class FeedbackRow(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    passage_id: Mapped[str] = mapped_column(String(36), index=True)
    rating: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearnerRow(Base):
    __tablename__ = "learners"
    __table_args__ = (UniqueConstraint("device_id", "language"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8))
    level: Mapped[str] = mapped_column(String(8), default="A2")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearnerLemmaRow(Base):
    __tablename__ = "learner_lemmas"
    __table_args__ = (UniqueConstraint("device_id", "language", "lemma"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8))
    lemma: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearnerStarRow(Base):
    __tablename__ = "learner_stars"
    __table_args__ = (UniqueConstraint("device_id", "language", "lemma"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8))
    lemma: Mapped[str] = mapped_column(String(120))
    gloss: Mapped[str | None] = mapped_column(String(200), nullable=True)
    passage_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearnerReadRow(Base):
    __tablename__ = "learner_reads"
    __table_args__ = (UniqueConstraint("device_id", "passage_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    passage_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.database_url.startswith("sqlite"):
        with engine.begin() as conn:
            cols = {row[1] for row in conn.execute(text("PRAGMA table_info(passages)"))}
            if "language" not in cols:
                conn.execute(
                    text("ALTER TABLE passages ADD COLUMN language VARCHAR(8) DEFAULT 'ru'")
                )
            if "translation" not in cols:
                conn.execute(text("ALTER TABLE passages ADD COLUMN translation TEXT"))
    from app.services.seed import seed_library

    seed_library()
