"""Add Setting model for maintenance mode

Revision ID: a6621a08d8c7
Revises: 7cbdb6dc05a6
Create Date: 2025-04-11 16:47:40.662445

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'a6621a08d8c7'
down_revision = '7cbdb6dc05a6'
branch_labels = None
depends_on = None


def upgrade():
    inspector = inspect(op.get_bind())
    table_names = set(inspector.get_table_names())
    if 'setting' in table_names:
        return
    if 'settings' not in table_names:
        op.create_table(
            'setting',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('key', sa.String(length=255), nullable=False),
            sa.Column('value', sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('key')
        )


def downgrade():
    pass
