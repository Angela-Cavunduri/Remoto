import os, sys
# Add project root to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.cruds.busca import buscar_por_nome
from app.database.connection import SessionLocal


def main():
    db = SessionLocal()
    for term in ['Angela', 'corte', 'servico']:
        results = buscar_por_nome(db, term)
        print(f"Search term: '{term}' -> {len(results)} results")
        for u in results:
            print(u.id_usuario, u.nome, getattr(u, 'rating_media', 'N/A'))

if __name__ == '__main__':
    main()
