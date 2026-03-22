"""add connected account model

Revision ID: 9d1b7a4f6c21
Revises: f2b8b0fd9a11
Create Date: 2026-03-21 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d1b7a4f6c21'
down_revision = 'f2b8b0fd9a11'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'connected_account',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=32), nullable=False),
        sa.Column('provider_account_id', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('profile_url', sa.String(length=500), nullable=True),
        sa.Column('connected_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_account_id', name='uq_connected_account_provider_account'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_connected_account_user_provider'),
    )


def downgrade():
    op.drop_table('connected_account')
