"""Learner choice to keep a daily news passage.

Revision ID: 0006_news_saves
Revises: 0005_placement_news
Create Date: 2026-09-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_news_saves"
down_revision = "0005_placement_news"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learner_news_saves",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("passage_id", sa.String(36), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("device_id", "passage_id"),
    )
    op.create_index("ix_learner_news_saves_device_id", "learner_news_saves", ["device_id"])
    op.create_index("ix_learner_news_saves_passage_id", "learner_news_saves", ["passage_id"])


def downgrade() -> None:
    op.drop_index("ix_learner_news_saves_passage_id", table_name="learner_news_saves")
    op.drop_index("ix_learner_news_saves_device_id", table_name="learner_news_saves")
    op.drop_table("learner_news_saves")
