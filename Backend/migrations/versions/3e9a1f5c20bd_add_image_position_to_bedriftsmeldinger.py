"""add image_position to bedriftsmeldinger

Revision ID: 3e9a1f5c20bd
Revises: 8f4c7d2b91aa
Create Date: 2026-04-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e9a1f5c20bd'
down_revision = '8f4c7d2b91aa'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bedriftsmeldinger', sa.Column('image_position', sa.String(length=100), nullable=True, server_default='center center'))


def downgrade():
    op.drop_column('bedriftsmeldinger', 'image_position')
