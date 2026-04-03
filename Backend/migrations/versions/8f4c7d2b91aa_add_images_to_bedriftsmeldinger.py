"""add image fields to bedriftsmeldinger

Revision ID: 8f4c7d2b91aa
Revises: c485eed56022
Create Date: 2026-04-03 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f4c7d2b91aa'
down_revision = 'c485eed56022'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('bedriftsmeldinger', sa.Column('image_url', sa.String(length=500), nullable=True))
    op.add_column('bedriftsmeldinger', sa.Column('image_alt', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('bedriftsmeldinger', 'image_alt')
    op.drop_column('bedriftsmeldinger', 'image_url')
