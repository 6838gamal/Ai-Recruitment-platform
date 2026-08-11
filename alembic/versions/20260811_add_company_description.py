"""add_company_description

Revision ID: 20260811_add_company_description
Revises: 4359233aaf6a
Create Date: 2026-08-11 06:40:00.000000+00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260811_add_company_description'
down_revision: Union[str, None] = '4359233aaf6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description column to companies (nullable to avoid migration pain)
    op.add_column('companies', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove description column on downgrade
    op.drop_column('companies', 'description')
