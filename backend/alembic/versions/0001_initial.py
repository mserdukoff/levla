"""Initial schema for accounts, catalog, SRS, trial events, and quota.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), unique=True),
        sa.Column("google_sub", sa.String(128), unique=True),
        sa.Column("display_name", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "magic_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), index=True),
        sa.Column("token", sa.String(64), unique=True, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "passages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("language", sa.String(8), index=True),
        sa.Column("level", sa.String(8), index=True),
        sa.Column("topic", sa.String(200)),
        sa.Column("genre", sa.String(40)),
        sa.Column("title", sa.String(300)),
        sa.Column("text", sa.Text()),
        sa.Column("tokens_json", sa.Text()),
        sa.Column("calibration_json", sa.Text()),
        sa.Column("word_count", sa.Integer()),
        sa.Column("translation", sa.Text()),
        sa.Column("shelf_status", sa.String(16), index=True),
        sa.Column("audio_url", sa.String(500)),
        sa.Column("audio_cues_json", sa.Text()),
        sa.Column("series_id", sa.String(64), index=True),
        sa.Column("chapter_index", sa.Integer()),
        sa.Column("comprehension_json", sa.Text()),
        sa.Column("topic_hash", sa.String(64), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("passage_id", sa.String(36), index=True),
        sa.Column("rating", sa.String(16)),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "learners",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True),
        sa.Column("language", sa.String(8)),
        sa.Column("level", sa.String(8)),
        sa.Column("consecutive_up", sa.Integer()),
        sa.Column("consecutive_down", sa.Integer()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("device_id", "language"),
    )
    op.create_table(
        "learner_lemmas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("language", sa.String(8)),
        sa.Column("lemma", sa.String(120)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("device_id", "language", "lemma"),
    )
    op.create_table(
        "learner_stars",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("language", sa.String(8)),
        sa.Column("lemma", sa.String(120)),
        sa.Column("gloss", sa.String(200)),
        sa.Column("reading", sa.String(200)),
        sa.Column("passage_id", sa.String(36)),
        sa.Column("context", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("device_id", "language", "lemma"),
    )
    op.create_table(
        "learner_reads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("passage_id", sa.String(36), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("device_id", "passage_id"),
    )
    op.create_table(
        "learner_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("language", sa.String(8)),
        sa.Column("lemma", sa.String(120)),
        sa.Column("gloss", sa.String(200)),
        sa.Column("reading", sa.String(200)),
        sa.Column("context", sa.Text()),
        sa.Column("passage_id", sa.String(36)),
        sa.Column("ease", sa.Float()),
        sa.Column("interval", sa.Integer()),
        sa.Column("reps", sa.Integer()),
        sa.Column("due_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("device_id", "language", "lemma"),
    )
    op.create_table(
        "trial_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(40), index=True),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("passage_id", sa.String(36), index=True),
        sa.Column("payload_json", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), index=True),
    )
    op.create_table(
        "generate_quota",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_key", sa.String(80), index=True),
        sa.Column("year_month", sa.String(7)),
        sa.Column("count", sa.Integer()),
        sa.UniqueConstraint("account_key", "year_month"),
    )
    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("status", sa.String(16), index=True),
        sa.Column("level", sa.String(8)),
        sa.Column("topic", sa.String(200)),
        sa.Column("genre", sa.String(40)),
        sa.Column("language", sa.String(8), index=True),
        sa.Column("known_lemmas_json", sa.Text()),
        sa.Column("device_id", sa.String(64), index=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("passage_id", sa.String(36)),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), index=True),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("generation_jobs")
    op.drop_table("generate_quota")
    op.drop_table("trial_events")
    op.drop_table("learner_cards")
    op.drop_table("learner_reads")
    op.drop_table("learner_stars")
    op.drop_table("learner_lemmas")
    op.drop_table("learners")
    op.drop_table("feedback")
    op.drop_table("passages")
    op.drop_table("magic_links")
    op.drop_table("users")
