"""init_table

Revision ID: d393a5ed888d
Revises: 
Create Date: 2025-10-09 23:36:39.652442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd393a5ed888d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('registration_date', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('avatar', sa.String(length=200), nullable=True),
    )

    op.create_table(
        'news',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('publication_date', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('cover', sa.String(length=200), nullable=True),
    )

    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('news_id', sa.Integer(), sa.ForeignKey('news.id'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('publication_date', sa.DateTime(), nullable=False, default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('comments')
    op.drop_table('news')
    op.drop_table('users')
