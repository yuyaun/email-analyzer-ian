"""create magic_task_results table

Revision ID: 0001_create_magic_task_results
Revises: 
Create Date: 2024-08-29
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_create_magic_task_results"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "magic_task_results",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("campaign_sn", sa.String(), nullable=True),
        sa.Column("magic_type", sa.String(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("magic_task_results")
