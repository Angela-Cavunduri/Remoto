from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/foto/{filename}")
def get_foto(filename: str):
    """Serve a profile photo stored in app/static/uploads/perfil/<filename>.

    The endpoint:
    - Removes any leading path prefix.
    - Normalizes duplicate extensions (e.g., .jpg.jpg, .png.png).
    - Validates that the file has an allowed image extension.
    - Returns 404 if the file does not exist.
    - Returns 400 if the extension is not supported.
    """
    # Remove potential path prefixes
    sanitized = filename
    prefix = "static/uploads/perfil/"
    if sanitized.startswith(prefix):
        sanitized = sanitized[len(prefix) :]
    elif sanitized.startswith("/" + prefix):
        sanitized = sanitized[len("/" + prefix) :]

    # Normalize duplicate extensions
    if sanitized.lower().endswith('.jpg.jpg'):
        sanitized = sanitized[:-4]
    if sanitized.lower().endswith('.png.png'):
        sanitized = sanitized[:-4]

    # Validate allowed extensions
    allowed_ext = {".jpg", ".jpeg", ".png"}
    _, ext = os.path.splitext(sanitized.lower())
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de imagem não suportado: '{ext}'. Use .jpg, .jpeg ou .png.",
        )

    file_path = os.path.join('app', 'static', 'uploads', 'perfil', sanitized)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(file_path)
