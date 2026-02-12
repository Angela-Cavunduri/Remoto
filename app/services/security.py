from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from passlib.exc import UnknownHashError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(password: str, hashed_password: str) -> str:
    try:
        return pwd_context.verify(password, hashed_password)
    except UnknownHashError:
        return "Senha incorreta"

SECRET_KEY="troca_fácil_super_secreta_123"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def create_access_token(data: dict):
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
