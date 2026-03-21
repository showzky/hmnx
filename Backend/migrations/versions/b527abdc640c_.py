"""empty message

Revision ID: b527abdc640c
Revises: da807ecc1eb9
Create Date: 2025-05-25 11:55:37.766294

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b527abdc640c'
down_revision = 'da807ecc1eb9'
branch_labels = None
depends_on = None


def upgrade():
    # This revision attempted to undo the achievement ID type change, but the
    # repository's canonical schema is finalized by
    # 96774187cc8b_fix_achievement_schema_properly. Keeping this as a no-op
    # avoids oscillating types during upgrade on MySQL.
    pass


def downgrade():
    pass
