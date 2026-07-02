import sys
import os

# Adiciona a raiz do projeto ao path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app.database.connection import engine
from sqlalchemy import text

queries = [
    # 1. Update ID 1 (TI)
    "UPDATE category SET nome = 'Tecnologia e Informática' WHERE id_category = 1;",
    "UPDATE servico SET id_category = 1 WHERE id_category IN (2, 6, 16, 18);",
    
    # 2. Update ID 3 (Reparações)
    "UPDATE category SET nome = 'Reparações e Manutenção' WHERE id_category = 3;",
    "UPDATE servico SET id_category = 3 WHERE id_category IN (4, 5, 9, 11);",
    
    # 3. Update ID 7 (Limpeza)
    "UPDATE category SET nome = 'Limpeza e Organização' WHERE id_category = 7;",
    "UPDATE servico SET id_category = 7 WHERE id_category IN (19);",
    
    # 4. Other renames
    "UPDATE category SET nome = 'Educação e Aulas Particulares' WHERE id_category = 8;",
    "UPDATE category SET nome = 'Casa e Jardinagem' WHERE id_category = 12;",
    "UPDATE category SET nome = 'Fotografia e Vídeo' WHERE id_category = 10;",
    "UPDATE category SET nome = 'Cuidados Infantis' WHERE id_category = 17;",
    "UPDATE category SET nome = 'Consultoria e Negócios' WHERE id_category = 15;",
    "UPDATE category SET nome = 'Saúde, Bem-estar e Fitness' WHERE id_category = 14;",
    "UPDATE category SET nome = 'Moda, Beleza e Estética' WHERE id_category = 13;",
    
    # Empty IDs now: 2, 4, 5, 6, 9, 11, 16, 18, 19
    "UPDATE category SET nome = 'Design e Criatividade' WHERE id_category = 2;",
    "UPDATE category SET nome = 'Transporte e Mudanças' WHERE id_category = 4;",
    "UPDATE category SET nome = 'Cuidados a Idosos' WHERE id_category = 5;",
    "UPDATE category SET nome = 'Cuidados com Animais' WHERE id_category = 6;",
    "UPDATE category SET nome = 'Alimentação e Catering' WHERE id_category = 9;",
    "UPDATE category SET nome = 'Música e Entretenimento' WHERE id_category = 11;",
    "UPDATE category SET nome = 'Entregas e Recados' WHERE id_category = 16;",
    "UPDATE category SET nome = 'Escrita, Tradução e Revisão de Textos' WHERE id_category = 18;",
    
    # Delete unused 19
    "DELETE FROM category WHERE id_category IN (19);"
]

try:
    with engine.begin() as conn:
        for q in queries:
            conn.execute(text(q))
    print('Categorias organizadas com sucesso!')
except Exception as e:
    print(f'Erro: {e}')
