"""add password, admin and token

Revision ID: 7cc88e948a47
Revises: d393a5ed888d
Create Date: 2025-10-16 00:30:21.689877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cc88e948a47'
down_revision: Union[str, Sequence[str], None] = 'd393a5ed888d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM comments"))
    connection.execute(sa.text("DELETE FROM news"))
    connection.execute(sa.text("DELETE FROM users"))
    
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('hashed_password', sa.String(256), nullable=True))

    op.create_table(
        "refresh_tokens",
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column('refresh_token', sa.String(length=128), unique=True, nullable=False),
        sa.Column('user_agent', sa.String(length=300)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )

def downgrade():
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'hashed_password')
    op.drop_table('refresh_tokens')
