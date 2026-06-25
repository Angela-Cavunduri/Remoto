import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Carrega variáveis de ambiente do .env (já carregado pelo app)
# Se estiver usando python-dotenv, pode ser carregado automaticamente; aqui usamos direto
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Construa a URL a partir das variáveis de MySQL presentes no .env
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST')
    db = os.getenv('MYSQL_DB')
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{db}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

prefix = '/static/uploads/perfil/'

with Session() as session:
    # Seleciona usuarios que têm o prefixo
    result = session.execute(text(
        "SELECT id_usuario, foto_perfil FROM usuario WHERE foto_perfil LIKE :p"
    ), {"p": f"{prefix}%"})
    rows = result.fetchall()
    print(f"Encontrados {len(rows)} registos a corrigir")
    for id_usuario, foto in rows:
        novo = foto.replace(prefix, '')
        session.execute(
            text("UPDATE usuario SET foto_perfil = :novo WHERE id_usuario = :id"),
            {"novo": novo, "id": id_usuario}
        )
    session.commit()
    print('Atualização concluída')
