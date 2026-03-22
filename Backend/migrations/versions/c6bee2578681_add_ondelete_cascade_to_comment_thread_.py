"""Add ondelete cascade to comment.thread_id

Revision ID: c6bee2578681
Revises: ef5637cb398e
Create Date: 2025-02-15 23:29:33.723031

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'c6bee2578681'
down_revision = 'ef5637cb398e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    foreign_keys = inspector.get_foreign_keys('comment')

    with op.batch_alter_table('comment', schema=None) as batch_op:
        for foreign_key in foreign_keys:
            if foreign_key.get('referred_table') == 'thread' and foreign_key.get('constrained_columns') == ['thread_id']:
                if foreign_key.get('name'):
                    batch_op.drop_constraint(foreign_key['name'], type_='foreignkey')
        batch_op.create_foreign_key('fk_comment_thread_id_thread', 'thread', ['thread_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comment_thread_id_thread', type_='foreignkey')
        batch_op.create_foreign_key('comment_ibfk_2', 'thread', ['thread_id'], ['id'])
