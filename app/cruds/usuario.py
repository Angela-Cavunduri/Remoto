from app.models.user import Usuario
from app.schemas.usuario import UsuarioCreate
from sqlalchemy.orm import Session
from app.services.security import hash_senha



def create_usuario(db: Session, usuario: UsuarioCreate):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise ValueError("Email já cadastrado")
        
        

    novo_usuario=Usuario(
    nome=usuario.nome,
    email=usuario.email,
    endereco=usuario.endereco,
    palavra_pass=hash_senha(usuario.palavra_pass)
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario