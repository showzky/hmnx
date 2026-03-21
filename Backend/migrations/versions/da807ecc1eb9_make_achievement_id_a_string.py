"""Make achievement_id a string

Revision ID: da807ecc1eb9
Revises: 0fe4f1eabc2f
Create Date: 2025-05-25 11:39:54.394149

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'da807ecc1eb9'
down_revision = '0fe4f1eabc2f'
branch_labels = None
depends_on = None


def upgrade():
    # This historical migration was incomplete for MySQL because it changed the
    # foreign-key column without first dropping the FK or converting
    # achievements.id. A later migration in this repo
    # (96774187cc8b_fix_achievement_schema_properly) performs the full schema
    # transition safely, so this step is intentionally a no-op.
    pass


def downgrade():
    pass
