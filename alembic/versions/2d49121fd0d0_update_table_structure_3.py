"""update table structure 3

Revision ID: 2d49121fd0d0
Revises: 0d097a42b025
Create Date: 2025-04-17 08:33:14.538136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2d49121fd0d0'
down_revision: Union[str, None] = '0d097a42b025'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_llms_id', table_name='llms')
    op.drop_table('llms')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('llms',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('provider', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('model', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('api_key', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('config', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='llms_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='llms_pkey')
    )
    op.create_index('ix_llms_id', 'llms', ['id'], unique=False)
    # ### end Alembic commands ###
