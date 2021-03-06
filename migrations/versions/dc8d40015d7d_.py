"""Add 'read' column

Revision ID: dc8d40015d7d
Revises: 798fb6c0c1d9
Create Date: 2019-10-01 21:52:12.613005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dc8d40015d7d"
down_revision = "798fb6c0c1d9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("note", sa.Column("read", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("note", "read")
