"""
Rotas de favoritos.

Este módulo contém endpoints para gerenciar produtos favoritos dos usuários.
"""
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from ..models import Favorite, Product, db
from ..constants import (
    ALLOWED_ORIGINS,
    SUCCESS_MESSAGES,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_UNAUTHORIZED,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_ERROR
)

logger = logging.getLogger(__name__)

favorite_bp = Blueprint("favorites", __name__)
CORS(favorite_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


@favorite_bp.route("/favorites", methods=["GET"])
@jwt_required()
def get_favorites():
    """
    Lista todos os produtos favoritos do usuário logado.
    
    Returns:
        200: Lista de produtos favoritos
        401: Usuário não autenticado
        500: Erro ao processar
    """
    user_id = get_jwt_identity()
    
    if not user_id:
        return jsonify({"error": "Usuário não autenticado"}), HTTP_UNAUTHORIZED

    try:
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        products = []

        for fav in favorites:
            product = Product.query.get(fav.product_id)
            if product:
                products.append(product.to_dict())

        logger.info(f"Usuário {user_id} consultou {len(products)} favoritos")
        
        return jsonify({
            "message": "Favoritos do usuário",
            "favorites": products
        }), HTTP_OK

    except Exception as e:
        logger.error(f"Erro em GET /favorites: {e}")
        return jsonify({"error": "Erro ao processar favoritos"}), HTTP_INTERNAL_ERROR


@favorite_bp.route("/favorites", methods=["POST", "OPTIONS"])
@jwt_required()
def add_favorite():
    """
    Adiciona um produto aos favoritos do usuário logado.
    
    Request Body:
        product_id (int): ID do produto
    
    Returns:
        201: Produto adicionado aos favoritos
        200: Produto já estava favoritado
        400: product_id não fornecido
        401: Usuário não autenticado
        500: Erro ao processar
    """
    if request.method == "OPTIONS":
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    user_id = get_jwt_identity()
    
    if not user_id:
        return jsonify({"error": "Usuário não autenticado"}), HTTP_UNAUTHORIZED

    try:
        data = request.get_json()
        product_id = data.get("product_id")
        
        if not product_id:
            return jsonify({"error": "product_id é obrigatório"}), HTTP_BAD_REQUEST

        # Verifica se já existe
        existing_fav = Favorite.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()
        
        if existing_fav:
            return jsonify({"message": "Produto já favoritado"}), HTTP_OK

        # Cria novo favorito
        new_fav = Favorite(
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.now()
        )
        db.session.add(new_fav)
        db.session.commit()

        logger.info(f"Usuário {user_id} favoritou produto {product_id}")
        
        return jsonify({
            "message": SUCCESS_MESSAGES['FAVORITE_ADDED']
        }), HTTP_CREATED

    except Exception as e:
        logger.error(f"Erro em POST /favorites: {e}")
        return jsonify({"error": "Erro ao processar favoritos"}), HTTP_INTERNAL_ERROR


@favorite_bp.route("/favorites/<int:product_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def remove_favorite(product_id):
    """
    Remove um produto dos favoritos do usuário logado.
    
    Path Parameters:
        product_id (int): ID do produto
    
    Returns:
        200: Produto removido dos favoritos
        404: Favorito não encontrado
        500: Erro ao processar
    """
    if request.method == "OPTIONS":
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    user_id = get_jwt_identity()

    try:
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        if not favorite:
            return jsonify({"error": "Favorito não encontrado"}), HTTP_NOT_FOUND

        db.session.delete(favorite)
        db.session.commit()

        logger.info(f"Usuário {user_id} removeu produto {product_id} dos favoritos")
        
        return jsonify({
            "message": SUCCESS_MESSAGES['FAVORITE_REMOVED']
        }), HTTP_OK

    except Exception as e:
        logger.error(f"Erro em DELETE /favorites/{product_id}: {e}")
        return jsonify({"error": "Erro ao remover favorito"}), HTTP_INTERNAL_ERROR
