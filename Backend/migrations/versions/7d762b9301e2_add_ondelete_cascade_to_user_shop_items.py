"""Add ondelete cascade to user_shop_items

Revision ID: 7d762b9301e2
Revises: 15c7f5b7d655
Create Date: 2025-05-02 22:51:41.612584

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '7d762b9301e2'
down_revision = '15c7f5b7d655'
branch_labels = None
depends_on = None


def upgrade():
    inspector = inspect(op.get_bind())
    foreign_keys = inspector.get_foreign_keys('user_shop_items')
    with op.batch_alter_table('user_shop_items', schema=None) as batch_op:
        for foreign_key in foreign_keys:
            if foreign_key.get('referred_table') == 'shop_items' and foreign_key.get('constrained_columns') == ['item_id']:
                if foreign_key.get('name'):
                    batch_op.drop_constraint(foreign_key['name'], type_='foreignkey')
        batch_op.create_foreign_key('fk_user_shop_items_item_id_shop_items', 'shop_items', ['item_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('user_shop_items', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_shop_items_item_id_shop_items', type_='foreignkey')
        batch_op.create_foreign_key('user_shop_items_ibfk_1', 'shop_items', ['item_id'], ['id'])
