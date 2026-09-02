"""Initial schema for accounts, catalog metadata, SRS, and trial events.

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


def downgrade() -> None:
    op.drop_table("passages")
    op.drop_table("users")
