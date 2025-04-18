"""update table structure

Revision ID: 229836e674d5
Revises: 56f7b7de5095
Create Date: 2025-04-17 08:25:08.561618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '229836e674d5'
down_revision: Union[str, None] = '56f7b7de5095'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_llms_id', table_name='llms')
    op.drop_table('llms')
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_foreign_key(None, 'users', 'companies', ['company_id'], ['id'])
    op.drop_column('users', 'company_size')
    op.drop_column('users', 'company_name')
    op.drop_column('users', 'company_industry')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('company_industry', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('company_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('company_size', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.alter_column('users', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('users', 'company_id')
    op.drop_column('users', 'is_active')
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
