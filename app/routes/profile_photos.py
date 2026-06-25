from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/foto/{filename}")
def get_foto(filename: str):
    """Serve a profile photo stored in app/static/uploads/perfil/<filename>."""
    # Strip any leading path segments that may already be present in the stored filename
    # e.g., 'static/uploads/perfil/angel.jpg' or '/static/uploads/perfil/angel.jpg'
    sanitized = filename
    prefix = "static/uploads/perfil/"
    if sanitized.startswith(prefix):
        sanitized = sanitized[len(prefix):]
    elif sanitized.startswith("/" + prefix):
        sanitized = sanitized[len("/" + prefix):]
    # Remove duplicate file extensions like '.jpg.jpg' or '.png.png'
    if sanitized.lower().endswith('.jpg.jpg'):
        sanitized = sanitized[:-4]
    if sanitized.lower().endswith('.png.png'):
        sanitized = sanitized[:-4]
    file_path = os.path.join('app', 'static', 'uploads', 'perfil', sanitized)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(file_path)
