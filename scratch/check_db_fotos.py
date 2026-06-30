import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database.connection import SessionLocal, engine
from app.models.user import Usuario

db = SessionLocal()
users = db.query(Usuario).all()
print(f"Total de usuários no banco de dados ativo ({engine.url}): {len(users)}")
for u in users:
    print(f"Usuario: {u.email}, foto_perfil: {u.foto_perfil}")
db.close()
