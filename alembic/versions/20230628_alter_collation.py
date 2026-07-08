"""alter collation for search fields

Revision ID: 20230628_alter_collation
Revises: 20230618_01_apply_schema_changes_safe
Create Date: 2026-06-28 15:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20230628_alter_collation"
down_revision = "20230618_01_apply_schema_changes_safe"
branch_labels = None
depends_on = None


def upgrade():
    # Usuario table
    op.execute(
        "ALTER TABLE Usuario MODIFY nome VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL"
    )
    op.execute(
        "ALTER TABLE Usuario MODIFY email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL"
    )
    # Servico table
    op.execute(
        "ALTER TABLE Servico MODIFY nome VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL"
    )
    op.execute(
        "ALTER TABLE Servico MODIFY descricao TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
    )
    # Add more tables/columns as needed


def downgrade():
    # Revert to previous collation (utf8mb4_unicode_ci)
    op.execute(
        "ALTER TABLE Usuario MODIFY nome VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL"
    )
    op.execute(
        "ALTER TABLE Usuario MODIFY email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL"
    )
    op.execute(
        "ALTER TABLE Servico MODIFY nome VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL"
    )
    op.execute(
        "ALTER TABLE Servico MODIFY descricao TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
