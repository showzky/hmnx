"""Add Setting model

Revision ID: be9b0f22a00c
Revises: a6621a08d8c7
Create Date: 2025-04-11 17:06:16.879315

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'be9b0f22a00c'
down_revision = 'a6621a08d8c7'
branch_labels = None
depends_on = None


def upgrade():
    inspector = inspect(op.get_bind())
    table_names = set(inspector.get_table_names())
    if 'settings' in table_names:
        indexes = {index['name'] for index in inspector.get_indexes('settings')}
        with op.batch_alter_table('settings', schema=None) as batch_op:
            if 'key' in indexes:
                batch_op.drop_index('key')
        op.drop_table('settings')


def downgrade():
    pass
