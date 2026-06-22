from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from app.database.connection import get_db
from app.models.user import Usuario

router = APIRouter(
    prefix="/cleanup",
    tags=["Cleanup"]
)

@router.get("/orphan-profile-images")
def cleanup_orphan_images(db: Session = Depends(get_db)):
    """Delete image files in static/uploads/perfil that are not referenced by any user.
    Returns the list of deleted file paths.
    """
    upload_dir = os.path.join('app', 'static', 'uploads', 'perfil')
    if not os.path.isdir(upload_dir):
        raise HTTPException(status_code=404, detail="Upload directory not found")
    referenced = set()
    users = db.query(Usuario).filter(Usuario.foto_perfil.isnot(None)).all()
    for user in users:
        if user.foto_perfil:
            filename = os.path.basename(user.foto_perfil)
            referenced.add(filename)
    deleted_files = []
    for fname in os.listdir(upload_dir):
        if fname not in referenced:
            fpath = os.path.join(upload_dir, fname)
            try:
                os.remove(fpath)
                deleted_files.append(f"/static/uploads/perfil/{fname}")
            except Exception:
                continue
    return {"deleted": deleted_files}
