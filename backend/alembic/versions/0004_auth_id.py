"""Link public.users to Supabase Auth.

Revision ID: 0004_auth_id
Revises: 0003_supabase_rls
Create Date: 2026-09-20
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_auth_id"
down_revision = "0003_supabase_rls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auth_id", sa.Uuid(), nullable=True))
    op.create_index("ix_users_auth_id", "users", ["auth_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_auth_id", table_name="users")
    op.drop_column("users", "auth_id")
