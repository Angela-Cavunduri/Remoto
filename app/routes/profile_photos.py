from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/foto/{filename}")
def get_foto(filename: str):
    """Serve a profile photo stored in app/static/uploads/perfil/<filename>."""
    file_path = os.path.join('app', 'static', 'uploads', 'perfil', filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(file_path)
