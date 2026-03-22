"""add discord_id to user

Revision ID: f2b8b0fd9a11
Revises: 96774187cc8b, c1f0d8e9b123
Create Date: 2026-03-21 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2b8b0fd9a11'
down_revision = ('96774187cc8b', 'c1f0d8e9b123')
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('discord_id', sa.String(length=32), nullable=True))
        batch_op.create_unique_constraint('uq_user_discord_id', ['discord_id'])


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_discord_id', type_='unique')
        batch_op.drop_column('discord_id')
