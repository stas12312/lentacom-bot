"""init

Revision ID: bd9042533eda
Revises: 
Create Date: 2021-10-07 18:52:22.203296

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bd9042533eda'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.BIGINT, primary_key=True),
    )

    op.create_table(
        'user_store',
        sa.Column('user_id', sa.BIGINT, sa.ForeignKey('users.id')),
        sa.Column('store_id', sa.VARCHAR(10)),
    )

    op.create_table(
        'user_skus',
        sa.Column('user_id', sa.BIGINT, sa.ForeignKey('users.id')),
        sa.Column('sku_id', sa.VARCHAR(10))
    )


def downgrade():
    op.drop_table('users')
    op.drop_table('user_store')
    op.drop_table('user_skus')
