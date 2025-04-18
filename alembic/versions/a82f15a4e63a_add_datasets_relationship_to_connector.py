"""Add datasets relationship to Connector

Revision ID: a82f15a4e63a
Revises: c55dcfd85c7e
Create Date: 2025-04-17 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a82f15a4e63a'
down_revision: Union[str, None] = 'c55dcfd85c7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type
    connectortype = postgresql.ENUM('POSTGRES', 'MYSQL', 'SQLITE', 'CSV', 'EXCEL', 'JSON', name='connectortype')
    connectortype.create(op.get_bind())

    # Add new columns
    op.add_column('connectors', sa.Column('description', sa.String(), nullable=True))
    op.add_column('connectors', sa.Column('config', sa.JSON(), nullable=True))
    op.add_column('connectors', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('connectors', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Update existing columns
    op.alter_column('connectors', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('connectors', 'type',
               existing_type=sa.VARCHAR(),
               type_=connectortype,
               postgresql_using='type::connectortype',
               nullable=True)

    # Create index
    op.create_index(op.f('ix_connectors_name'), 'connectors', ['name'], unique=True)


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_connectors_name'), table_name='connectors')

    # Drop columns
    op.drop_column('connectors', 'updated_at')
    op.drop_column('connectors', 'created_at')
    op.drop_column('connectors', 'config')
    op.drop_column('connectors', 'description')

    # Revert type changes
    op.alter_column('connectors', 'type',
               existing_type=postgresql.ENUM('POSTGRES', 'MYSQL', 'SQLITE', 'CSV', 'EXCEL', 'JSON', name='connectortype'),
               type_=sa.VARCHAR(),
               postgresql_using='type::varchar',
               nullable=False)
    op.alter_column('connectors', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # Drop the enum type
    connectortype = postgresql.ENUM('POSTGRES', 'MYSQL', 'SQLITE', 'CSV', 'EXCEL', 'JSON', name='connectortype')
    connectortype.drop(op.get_bind())
