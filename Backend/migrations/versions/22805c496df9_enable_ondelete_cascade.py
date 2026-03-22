"""Enable ondelete cascade

Revision ID: 22805c496df9
Revises: c6bee2578681
Create Date: 2025-02-16 00:14:43.133664

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '22805c496df9'
down_revision = 'c6bee2578681'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    foreign_keys = inspector.get_foreign_keys('comment')

    with op.batch_alter_table('comment', schema=None) as batch_op:
        for foreign_key in foreign_keys:
            if foreign_key.get('referred_table') == 'comment' and foreign_key.get('constrained_columns') == ['parent_id']:
                if foreign_key.get('name'):
                    batch_op.drop_constraint(foreign_key['name'], type_='foreignkey')
        batch_op.create_foreign_key('fk_comment_parent_id_comment', 'comment', ['parent_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comment_parent_id_comment', type_='foreignkey')
        batch_op.create_foreign_key('comment_ibfk_1', 'comment', ['parent_id'], ['id'])
