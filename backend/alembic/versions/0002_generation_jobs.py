"""Async generation job queue.

Revision ID: 0002_generation_jobs
Revises: 0001_initial
Create Date: 2026-09-03
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_generation_jobs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "generation_jobs" in insp.get_table_names():
        return
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
