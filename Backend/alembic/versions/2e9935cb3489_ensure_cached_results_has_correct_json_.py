"""Ensure cached_results has correct JSON type for response

Revision ID: 2e9935cb3489
Revises: 39ffb69f7735
Create Date: 2025-01-30 16:30:32.965268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e9935cb3489'
down_revision: Union[str, None] = '39ffb69f7735'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1) Delete all rows from 'cached_results' (destructive!)
    2) Alter column 'response' to JSON with explicit cast
    """
    # 1) Delete all rows
    op.execute("DELETE FROM cached_results;")

    # 2) Now that table is empty, change column type from TEXT to JSON
    #    (no invalid JSON left to cause errors)
    op.execute("""
        ALTER TABLE cached_results
        ALTER COLUMN response TYPE JSON USING response::json;
    """)


def downgrade() -> None:
    """
    Revert 'response' column back to TEXT.
    (You won't get the deleted data back, obviously.)
    """
    # Revert column type to TEXT
    op.execute("""
        ALTER TABLE cached_results
        ALTER COLUMN response TYPE TEXT USING response::text;
    """)