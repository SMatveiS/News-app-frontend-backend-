"""increase_refresh_token_length

Revision ID: 70a72eb10257
Revises: 7cc88e948a47
Create Date: 2025-10-26 20:54:47.656626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70a72eb10257'
down_revision: Union[str, Sequence[str], None] = '7cc88e948a47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('refresh_tokens', 'refresh_token',
                    type_=sa.String(512),
                    existing_type=sa.String(128))

def downgrade():
    op.alter_column('refresh_tokens', 'refresh_token',
                    type_=sa.String(128),
                    existing_type=sa.String(512))