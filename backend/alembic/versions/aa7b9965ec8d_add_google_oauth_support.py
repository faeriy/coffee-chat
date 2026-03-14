"""add_google_oauth_support

Revision ID: aa7b9965ec8d
Revises: a89e720a18f2
Create Date: 2026-03-13 21:18:00.781541

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aa7b9965ec8d"
down_revision: Union[str, Sequence[str], None] = "a89e720a18f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add google_id for OAuth, allow null password for Google-only users."""
    op.add_column("users", sa.Column("google_id", sa.String(), nullable=True))
    op.create_index(op.f("ix_users_google_id"), "users", ["google_id"], unique=True)
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(),
        nullable=False,
    )
    op.drop_index(op.f("ix_users_google_id"), table_name="users")
    op.drop_column("users", "google_id")
