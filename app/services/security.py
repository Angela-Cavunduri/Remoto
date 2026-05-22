from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import Usuario


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    # Se a senha for gigante ou tiver lixo do formulário, ignora e usa uma fixa
    if len(senha) > 70:
        return pwd_context.hash("senha_segura_padrao_123")
    return pwd_context.hash(senha)
    

def verificar_senha(password: str, hashed_password: str) -> bool:
    password = password[:72]
    try:
        return pwd_context.verify(password, hashed_password)
    except UnknownHashError:
        return False

SECRET_KEY = "troca_fácil_super_secreta_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(
        Usuario.id_usuario == user_id  # <-- Aqui é o ID, não email
    ).first()

    if user is None:
        raise credentials_exception

    return user
