"""add_store_and_skus_unique

Revision ID: bbe6561db2a9
Revises: 369cdc4c1358
Create Date: 2021-10-28 20:19:11.557601

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bbe6561db2a9'
down_revision = '369cdc4c1358'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("user_store_user_id_unique", "user_store", ["user_id"])
    op.create_unique_constraint("user_skus_user_id_unique", "user_skus", ["user_id", "sku_id"])


def downgrade():
    op.drop_constraint("user_store_user_id_unique", "user_store")
    op.drop_constraint("user_skus_user_id_unique", "user_skus")
