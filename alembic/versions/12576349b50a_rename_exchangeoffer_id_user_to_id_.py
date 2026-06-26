"""rename ExchangeOffer.id_user to id_usuario_destinatario

Revision ID: 12576349b50a
Revises: 20230618_01_apply_schema_changes_safe
Create Date: 2026-06-26 18:21:48.803806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12576349b50a'
down_revision: Union[str, Sequence[str], None] = '20230618_01_apply_schema_changes_safe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exchangeoffer") as batch_op:
        batch_op.alter_column(
            "id_user",
            new_column_name="id_usuario_destinatario",
            existing_type=sa.Integer,
            nullable=False,
        )
        batch_op.drop_constraint("exchangeoffer_ibfk_1", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_exchangeoffer_id_usuario_destinatario_usuario",
            "usuario",
            ["id_usuario_destinatario"],
            ["id_usuario"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("exchangeoffer") as batch_op:
        batch_op.alter_column(
            "id_usuario_destinatario",
            new_column_name="id_user",
            existing_type=sa.Integer,
            nullable=False,
        )
        batch_op.drop_constraint(
            "fk_exchangeoffer_id_usuario_destinatario_usuario", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "exchangeoffer_ibfk_1",
            "usuario",
            ["id_user"],
            ["id_usuario"],
            ondelete="CASCADE",
        )
