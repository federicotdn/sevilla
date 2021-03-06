"""initial migration

Revision ID: 798fb6c0c1d9
Revises:
Create Date: 2019-09-18 21:27:49.457489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "798fb6c0c1d9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "note",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("contents", sa.Text(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "token",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("expiration", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("token")
    op.drop_table("note")
