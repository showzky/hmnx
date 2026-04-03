"""add show_countdown to event

Revision ID: a1b2c3d4e5f6
Revises: 7d2bf787c98f
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '7d2bf787c98f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('event', sa.Column('show_countdown', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('event', 'show_countdown')
