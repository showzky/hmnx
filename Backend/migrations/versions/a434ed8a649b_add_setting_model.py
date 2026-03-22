"""Add Setting model

Revision ID: a434ed8a649b
Revises: be9b0f22a00c
Create Date: 2025-04-11 21:47:19.928960

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'a434ed8a649b'
down_revision = 'be9b0f22a00c'
branch_labels = None
depends_on = None


def upgrade():
    inspector = inspect(op.get_bind())
    if 'setting' not in set(inspector.get_table_names()):
        op.create_table('setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
        )


def downgrade():
    inspector = inspect(op.get_bind())
    if 'setting' in set(inspector.get_table_names()):
        op.drop_table('setting')
