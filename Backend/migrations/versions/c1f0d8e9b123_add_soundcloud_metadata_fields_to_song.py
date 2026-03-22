"""add soundcloud metadata fields to song

Revision ID: c1f0d8e9b123
Revises: 948b2ce5777f
Create Date: 2026-03-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1f0d8e9b123'
down_revision = '948b2ce5777f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.add_column(sa.Column('url', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('author_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('thumbnail_url', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('featured', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('song', schema=None) as batch_op:
        batch_op.drop_column('featured')
        batch_op.drop_column('duration')
        batch_op.drop_column('thumbnail_url')
        batch_op.drop_column('author_name')
        batch_op.drop_column('url')
