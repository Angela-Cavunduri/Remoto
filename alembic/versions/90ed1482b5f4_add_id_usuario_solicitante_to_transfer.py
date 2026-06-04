"""add_id_usuario_solicitante_to_transfer

Revision ID: 90ed1482b5f4
Revises: 681517a6c91f
Create Date: 2026-06-04 14:31:42.799762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '90ed1482b5f4'
down_revision: Union[str, Sequence[str], None] = '681517a6c91f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona a nova coluna id_usuario_solicitante à tabela transfer
    op.add_column('transfer', sa.Column('id_usuario_solicitante', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'transfer', 'usuario', ['id_usuario_solicitante'], ['id_usuario'])


def downgrade() -> None:
    op.drop_constraint(None, 'transfer', type_='foreignkey')
    op.drop_column('transfer', 'id_usuario_solicitante')
