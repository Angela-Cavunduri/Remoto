from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.database.connection import engine

router = APIRouter(prefix="/debug", tags=["Debug Utilities"])

@router.post("/collation")
async def apply_accent_insensitive_collation():
    """
    Executa ALTER TABLE para tornar as colunas de texto
    accent‑insensitive (utf8mb4_0900_ai_ci).
    Uso: apenas em desenvolvimento ou ambiente controlado.
    """
    statements = [
        "ALTER TABLE Usuario MODIFY nome VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL",
        "ALTER TABLE Usuario MODIFY email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL",
        "ALTER TABLE Servico MODIFY nome VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL",
        "ALTER TABLE Servico MODIFY descricao TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
    ]
    try:
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to apply collation: {exc}")
    return {"success": true, "message": "Collation altered successfully"}
