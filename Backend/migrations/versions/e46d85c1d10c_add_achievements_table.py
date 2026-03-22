"""Add achievements table

Revision ID: e46d85c1d10c
Revises: 8b32c27f7e55
Create Date: 2025-05-24 10:13:14.383365

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'e46d85c1d10c'
down_revision = '8b32c27f7e55'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('achievements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('icon', sa.Text(), nullable=True),
    sa.Column('rarity', sa.String(length=50), nullable=True),
    sa.Column('glow_color', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    inspector = inspect(op.get_bind())
    foreign_keys = inspector.get_foreign_keys('user_achievements')
    with op.batch_alter_table('user_achievements', schema=None) as batch_op:
        for foreign_key in foreign_keys:
            if foreign_key.get('constrained_columns') == ['achievement_id'] and foreign_key.get('name'):
                batch_op.drop_constraint(foreign_key['name'], type_='foreignkey')
        batch_op.create_foreign_key('fk_user_achievements_achievement_id_achievements', 'achievements', ['achievement_id'], ['id'])


def downgrade():
    with op.batch_alter_table('user_achievements', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_achievements_achievement_id_achievements', type_='foreignkey')
        batch_op.create_foreign_key('user_achievements_ibfk_1', 'shop_items', ['achievement_id'], ['id'])

    op.drop_table('achievements')
