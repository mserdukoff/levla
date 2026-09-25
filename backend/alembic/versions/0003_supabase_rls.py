"""Lock down the public schema for Supabase Data API.

Revision ID: 0003_supabase_rls
Revises: 0002_generation_jobs
Create Date: 2026-09-20
"""

from alembic import op

from app.models.db import lock_down_public_schema

revision = "0003_supabase_rls"
down_revision = "0002_generation_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    lock_down_public_schema(bind)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        """
        DO $$
        DECLARE
          r text;
        BEGIN
          FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
              EXECUTE format('GRANT USAGE ON SCHEMA public TO %I', r);
              EXECUTE format('GRANT ALL ON ALL TABLES IN SCHEMA public TO %I', r);
              EXECUTE format('GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO %I', r);
            END IF;
          END LOOP;
        END $$;
        """
    )
