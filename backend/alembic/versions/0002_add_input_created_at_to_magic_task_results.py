"""add input and created_at to magic_task_results table

Revision ID: 0002_add_input_created_at_to_magic_task_results
Revises: 0001_create_magic_task_results
Create Date: 2024-08-30
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_add_input_created_at"
down_revision = "0001_create_magic_task_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 `input` 與 `created_at` 欄位。"""
    op.add_column("magic_task_results", sa.Column("input", sa.Text(), nullable=True))
    op.add_column(
        "magic_task_results",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """移除 `input` 與 `created_at` 欄位。"""
    op.drop_column("magic_task_results", "created_at")
    op.drop_column("magic_task_results", "input")
