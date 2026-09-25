"""Placement flag, gloss taps, and daily news issues.

Revision ID: 0005_placement_news
Revises: 0004_auth_id
Create Date: 2026-09-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_placement_news"
down_revision = "0004_auth_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "learners",
        sa.Column("placed", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("passages", sa.Column("source_name", sa.String(120), nullable=True))
    op.add_column("passages", sa.Column("source_url", sa.String(500), nullable=True))
    op.add_column("passages", sa.Column("source_date", sa.String(32), nullable=True))
    op.create_table(
        "learner_taps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("lemma", sa.String(120), nullable=False),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("device_id", "language", "lemma"),
    )
    op.create_index("ix_learner_taps_device_id", "learner_taps", ["device_id"])
    op.create_index("ix_learner_taps_seen_at", "learner_taps", ["seen_at"])
    op.create_table(
        "news_issues",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("issue_date", sa.String(10), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("level", sa.String(8), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("passage_id", sa.String(36), nullable=True),
        sa.Column("source_name", sa.String(120), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("headline", sa.String(300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("issue_date", "language", "level"),
    )
    op.create_index("ix_news_issues_issue_date", "news_issues", ["issue_date"])
    op.create_index("ix_news_issues_language", "news_issues", ["language"])
    op.create_index("ix_news_issues_status", "news_issues", ["status"])


def downgrade() -> None:
    op.drop_index("ix_news_issues_status", table_name="news_issues")
    op.drop_index("ix_news_issues_language", table_name="news_issues")
    op.drop_index("ix_news_issues_issue_date", table_name="news_issues")
    op.drop_table("news_issues")
    op.drop_index("ix_learner_taps_seen_at", table_name="learner_taps")
    op.drop_index("ix_learner_taps_device_id", table_name="learner_taps")
    op.drop_table("learner_taps")
    op.drop_column("passages", "source_date")
    op.drop_column("passages", "source_url")
    op.drop_column("passages", "source_name")
    op.drop_column("learners", "placed")
