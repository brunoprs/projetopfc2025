"""
Rotas de avaliações e notas de produtos.

Este módulo contém endpoints para gerenciar comentários e ratings de produtos.
"""
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from ..models import Review, User, db
from ..constants import (
    ALLOWED_ORIGINS,
    SUCCESS_MESSAGES,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND
)

logger = logging.getLogger(__name__)

review_bp = Blueprint("reviews", __name__)
CORS(review_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


# Importa funções de moderação de conteúdo (se disponíveis)
try:
    from ..utils.banned_words import contains_banned_word, censor_text
except Exception:
    def contains_banned_word(text: str) -> bool:
        return False
    
    def censor_text(text: str) -> str:
        return text


# ===================================
# COMENTÁRIOS (REVIEWS)
# ===================================

@review_bp.route('/products/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """
    Lista todos os comentários de um produto.
    
    Path Parameters:
        product_id (int): ID do produto
    
    Returns:
        200: Lista de comentários com dados do usuário
    """
    reviews = Review.query.filter_by(product_id=product_id).join(User).add_columns(
        Review.id,
        Review.user_id,
        User.name,
        Review.comment,
        Review.created_at
    ).order_by(Review.created_at.desc()).all()
    
    review_list = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "user_name": r.name,
            "comment": r.comment,
            "created_at": r.created_at.strftime('%d/%m/%Y %H:%M') if r.created_at else None
        }
        for r in reviews
    ]
    
    return jsonify(review_list), HTTP_OK


@review_bp.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(product_id):
    """
    Adiciona um comentário a um produto.
    
    Path Parameters:
        product_id (int): ID do produto
    
    Request Body:
        comment (str): Texto do comentário
    
    Returns:
        201: Comentário adicionado com sucesso
        400: Comentário vazio ou contém palavras proibidas
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    comment = data.get('comment', '').strip()

    if not comment:
        return jsonify({'error': 'Comentário é obrigatório'}), HTTP_BAD_REQUEST

    # Verifica palavras proibidas
    if contains_banned_word(comment):
        return jsonify({
            'error': 'Comentário contém palavras não permitidas. Por favor, revise seu texto.'
        }), HTTP_BAD_REQUEST

    new_review = Review(
        product_id=product_id,
        user_id=current_user_id,
        comment=comment,
        created_at=datetime.utcnow()
    )
    db.session.add(new_review)
    db.session.commit()

    logger.info(f"Usuário {current_user_id} comentou no produto {product_id}")
    
    return jsonify({
        'message': SUCCESS_MESSAGES['REVIEW_SUBMITTED']
    }), HTTP_CREATED


@review_bp.route('/products/<int:product_id>/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(product_id, review_id):
    """
    Exclui um comentário (apenas o autor ou admin).
    
    Path Parameters:
        product_id (int): ID do produto
        review_id (int): ID do comentário
    
    Returns:
        200: Comentário deletado com sucesso
        401: Usuário não encontrado
        403: Não autorizado
        404: Comentário não encontrado
    """
    user_id = int(get_jwt_identity())
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), HTTP_UNAUTHORIZED

    review = Review.query.filter_by(id=review_id, product_id=product_id).first()
    if not review:
        return jsonify({"error": "Comentário não encontrado"}), HTTP_NOT_FOUND

    # Apenas o autor ou admin podem deletar
    if review.user_id != user.id and not user.is_admin:
        return jsonify({
            "error": "Não autorizado a deletar este comentário"
        }), HTTP_FORBIDDEN

    db.session.delete(review)
    db.session.commit()
    
    logger.info(f"Comentário {review_id} deletado por usuário {user_id}")
    
    return jsonify({"message": "Comentário deletado com sucesso"}), HTTP_OK


# ===================================
# NOTAS (RATINGS)
# ===================================

@review_bp.route('/products/<int:product_id>/rating', methods=['POST'])
@jwt_required()
def rate_product(product_id):
    """
    Atribui ou atualiza uma nota (1-5) para um produto.
    
    Path Parameters:
        product_id (int): ID do produto
    
    Request Body:
        rating (int): Nota de 1 a 5
    
    Returns:
        200: Nota registrada com sucesso
        400: Nota inválida
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    rating = data.get('rating')

    # Valida faixa de nota
    if rating is None or not (1 <= rating <= 5):
        return jsonify({'error': 'A nota deve ser entre 1 e 5'}), HTTP_BAD_REQUEST

    # Atualiza se já existe, senão cria novo
    review = Review.query.filter_by(product_id=product_id, user_id=user_id).first()

    if review:
        review.rating = rating
        review.created_at = datetime.utcnow()
        logger.info(f"Usuário {user_id} atualizou nota do produto {product_id} para {rating}")
    else:
        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            created_at=datetime.utcnow()
        )
        db.session.add(review)
        logger.info(f"Usuário {user_id} avaliou produto {product_id} com nota {rating}")

    db.session.commit()
    
    return jsonify({
        'message': SUCCESS_MESSAGES['RATING_SUBMITTED']
    }), HTTP_OK


@review_bp.route('/products/<int:product_id>/rating', methods=['GET'])
def get_product_rating(product_id):
    """
    Retorna a média de notas de um produto.
    
    Path Parameters:
        product_id (int): ID do produto
    
    Returns:
        200: Média e contagem de avaliações
    """
    ratings = Review.query.filter_by(product_id=product_id).with_entities(Review.rating).all()
    
    if not ratings:
        return jsonify({'average': None, 'count': 0}), HTTP_OK

    values = [r.rating for r in ratings if r.rating is not None]
    
    if not values:
        return jsonify({'average': None, 'count': 0}), HTTP_OK

    # Calcula média com uma casa decimal
    avg = round(sum(values) / len(values), 1)
    
    return jsonify({'average': avg, 'count': len(values)}), HTTP_OK
