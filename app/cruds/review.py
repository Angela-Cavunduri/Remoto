from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.exchangeOffer import ExchangeOffer
from app.models.review import Review
from app.models.user import Usuario


def create_review(db: Session, dados, current_user):
    # 1. Validações Iniciais
    oferta = db.query(ExchangeOffer).filter(
        ExchangeOffer.id_offer == dados.id_exchange_offer
    ).first()

    if not oferta:
        raise HTTPException(404, "Troca não encontrada")
    
    if oferta.status != "concluida":
        raise HTTPException(400, "Só pode avaliar após a troca ser concluída.")

    # Verificar se quem está a avaliar faz parte da troca
    if current_user.id_usuario not in [oferta.id_user, oferta.id_usuario_solicitante]:
        raise HTTPException(403, "Não faz parte desta troca para poder avaliar.")

    # Verificar se já avaliou
    review_existente = db.query(Review).filter(
        Review.id_exchange_offer == dados.id_exchange_offer,
        Review.id_avaliador == current_user.id_usuario
    ).first()

    if review_existente:
        raise HTTPException(400, "Você já avaliou nesta troca.")

    # 2. Criar a Avaliação
    nova_review = Review(
        id_exchange_offer=dados.id_exchange_offer,
        id_avaliado=dados.id_avaliado,
        id_avaliador=current_user.id_usuario,
        avaliacao=dados.avaliacao,
        conteudo=dados.conteudo
    )
    db.add(nova_review)
    db.flush()

    # 3. Atualizar a Média do Utilizador Avaliado
    avaliado = db.query(Usuario).filter(Usuario.id_usuario == dados.id_avaliado).first()
    todas_avaliacoes = db.query(Review).filter(Review.id_avaliado == dados.id_avaliado).all()
    
    if todas_avaliacoes:
        media = sum(r.avaliacao for r in todas_avaliacoes) / len(todas_avaliacoes)
        avaliado.rating_media = round(media) # Guardamos como inteiro para facilitar, ou float se preferir
    
    # 4. Verificar se deve ser expulso (mais de 3 estrelas negativas: 1 ou 2)
    avaliacoes_negativas = [r for r in todas_avaliacoes if r.avaliacao <= 2]
    if len(avaliacoes_negativas) >= 3:
        avaliado.is_active = False # Banimento automático
        # Opcional: Cancelar serviços do utilizador banido
        from app.models.servico import Servico
        db.query(Servico).filter(Servico.id_user == avaliado.id_usuario).update({"status": "inativo"})

    db.commit()
    db.refresh(nova_review)
    return nova_review
    
def concluir_oferta(db: Session, offer_id: int, current_user):

    oferta = db.query(ExchangeOffer).filter(
        ExchangeOffer.id_offer == offer_id
    ).first()
    if oferta.servico_desejado.id_user != current_user.id_usuario:
        raise HTTPException(
            403,
            "Só o dono do serviço pode concluir a troca"
        )
    if oferta.status != "aceita":
        raise HTTPException(
            400,
            "Só ofertas aceitas podem ser concluídas"
        )
    oferta.status = "concluida"
    db.commit()
    db.refresh(oferta)
    return oferta