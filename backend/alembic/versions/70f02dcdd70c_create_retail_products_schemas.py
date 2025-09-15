"""create retail products schemas

Revision ID: 70f02dcdd70c
Revises: 3ad9ba346a41
Create Date: 2025-09-08 10:08:49.262974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70f02dcdd70c'
down_revision: Union[str, Sequence[str], None] = '3ad9ba346a41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
