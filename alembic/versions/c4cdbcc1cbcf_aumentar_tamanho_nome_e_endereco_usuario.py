"""aumentar_tamanho_nome_e_endereco_usuario

Revision ID: c4cdbcc1cbcf
Revises: 90ed1482b5f4
Create Date: 2026-06-09 15:45:54.832445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
"""aumentar_tamanho_nome_e_endereco_usuario

Revision ID: c4cdbcc1cbcf
Revises: 90ed1482b5f4
Create Date: 2026-06-09 15:45:54.832445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c4cdbcc1cbcf'
down_revision: Union[str, Sequence[str], None] = '90ed1482b5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('usuario', 'nome',
               existing_type=sa.String(length=50),
               type_=sa.String(length=150),
               existing_nullable=False)
    op.alter_column('usuario', 'endereco',
               existing_type=sa.String(length=50),
               type_=sa.String(length=255),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('usuario', 'endereco',
               existing_type=sa.String(length=255),
               type_=sa.String(length=50),
               existing_nullable=False)
    op.alter_column('usuario', 'nome',
               existing_type=sa.String(length=150),
               type_=sa.String(length=50),
               existing_nullable=False)
