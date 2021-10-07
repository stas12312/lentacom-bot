"""Add user info

Revision ID: 369cdc4c1358
Revises: bd9042533eda
Create Date: 2021-10-07 21:53:25.882796

"""
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy import func, text

revision = '369cdc4c1358'
down_revision = 'bd9042533eda'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('first_name', sa.VARCHAR(100)))
    op.add_column('users', sa.Column('last_name', sa.VARCHAR(100)))
    op.add_column('users', sa.Column('created_at', sa.TIMESTAMP, server_default=func.now()))


def downgrade():
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'created_at')
