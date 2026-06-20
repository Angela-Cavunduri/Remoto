'''alembic revision
Revision ID: 20230618_01_apply_schema_changes_safe
Revises: f3e98805bfa4
Create Date: 2026-06-18 21:15:00.000000
'''

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20230618_01_apply_schema_changes_safe'
down_revision = 'f3e98805bfa4'
branch_labels = None
depends_on = None

def upgrade():
    # -------------------------------------------------
    # Servico: garantir que data_criacao não seja NULL
    # -------------------------------------------------
    # Preencher valores nulos com timestamp atual
    op.execute(
        "UPDATE servico SET data_criacao = NOW() WHERE data_criacao IS NULL"
    )
    # Alterar coluna para NOT NULL com default CURRENT_TIMESTAMP
    op.alter_column('servico', 'data_criacao',
                    existing_type=sa.DateTime(),
                    nullable=False,
                    server_default=sa.func.current_timestamp())

    # -------------------------------------------------
    # Transfer: remover NULLs e definir defaults
    # -------------------------------------------------
    # Caso existam registros, definir valores plausíveis (0) –
    # Na prática a tabela deve estar vazia; se houver, será
    # necessário ajustá‑los manualmente.
    op.execute(
        "UPDATE transfer SET id_user = 0 WHERE id_user IS NULL"
    )
    op.execute(
        "UPDATE transfer SET id_usuario_solicitante = 0 WHERE id_usuario_solicitante IS NULL"
    )
    op.execute(
        "UPDATE transfer SET id_exchangeoffer = 0 WHERE id_exchangeoffer IS NULL"
    )
    # Garantir data_datroca não nula
    op.execute(
        "UPDATE transfer SET data_datroca = NOW() WHERE data_datroca IS NULL"
    )
    # Garantir estado não nulo
    op.execute(
        "UPDATE transfer SET estados = 'em andamento' WHERE estados IS NULL"
    )
    # Alterar colunas para NOT NULL
    op.alter_column('transfer', 'id_user', existing_type=sa.Integer(), nullable=False)
    op.alter_column('transfer', 'id_usuario_solicitante', existing_type=sa.Integer(), nullable=False)
    op.alter_column('transfer', 'id_exchangeoffer', existing_type=sa.Integer(), nullable=False)
    op.alter_column('transfer', 'data_datroca', existing_type=sa.DateTime(), nullable=False)
    op.alter_column('transfer', 'estados', existing_type=sa.String(length=50), nullable=False)

    # -------------------------------------------------
    # ExchangeOffer: garantir que mensagem possa ser NULL
    # -------------------------------------------------
    op.alter_column('exchangeoffer', 'mensagem',
                    existing_type=sa.String(length=255),
                    nullable=True,
                    existing_server_default=None)

def downgrade():
    # Reverter as alterações (cuidado: dados podem ser perdidos)
    op.alter_column('servico', 'data_criacao', nullable=True, server_default=None)
    op.alter_column('transfer', 'id_user', nullable=True)
    op.alter_column('transfer', 'id_usuario_solicitante', nullable=True)
    op.alter_column('transfer', 'id_exchangeoffer', nullable=True)
    op.alter_column('transfer', 'data_datroca', nullable=True)
    op.alter_column('transfer', 'estados', nullable=True)
    op.alter_column('exchangeoffer', 'mensagem', nullable=False)
