"""merge image_position and connected_accounts heads

Revision ID: 7d2bf787c98f
Revises: 3e9a1f5c20bd, 9d1b7a4f6c21
Create Date: 2026-04-03 02:56:29.133072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d2bf787c98f'
down_revision = ('3e9a1f5c20bd', '9d1b7a4f6c21')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
