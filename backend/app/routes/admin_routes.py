"""
Rotas administrativas (dashboard, gerenciamento de usuários, estatísticas).

Este módulo contém endpoints exclusivos para administradores.
"""
import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import func, or_
from ..decorators import admin_required, master_admin_required
from ..services import AuthService
from ..models import User, Product, Tip, Review, Favorite, FAQ, SocialMedia, db
from ..constants import (
    ALLOWED_ORIGINS,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    HTTP_BAD_REQUEST,
    HTTP_FORBIDDEN,
    HTTP_INTERNAL_ERROR
)

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)
CORS(admin_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


# ===================================
# ESTATÍSTICAS E DASHBOARD
# ===================================

@admin_bp.route("/admin/stats", methods=["GET"])
@jwt_required()
@admin_required
def get_admin_stats():
    """
    Retorna estatísticas gerais do sistema.
    
    Returns:
        200: Estatísticas (total de produtos, usuários, dicas, reviews, favoritos)
        500: Erro ao buscar estatísticas
    """
    try:
        total_products = Product.query.count()
        total_users = User.query.count()
        total_tips = Tip.query.count()
        total_reviews = Review.query.count()
        total_favorites = Favorite.query.count()

        return jsonify({
            "total_products": total_products,
            "total_users": total_users,
            "total_tips": total_tips,
            "total_reviews": total_reviews,
            "total_favorites": total_favorites
        }), HTTP_OK
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({"error": "Erro ao buscar estatísticas"}), HTTP_INTERNAL_ERROR


@admin_bp.route("/admin/user-growth", methods=["GET"])
@jwt_required()
@admin_required
def get_user_growth():
    """
    Retorna crescimento de usuários por mês.
    
    Returns:
        200: Lista com crescimento por ano/mês
        500: Erro ao buscar dados
    """
    try:
        growth_data = User.get_growth_by_month()
        
        formatted_data = [
            {"year": int(year), "month": int(month), "total": total}
            for year, month, total in growth_data
        ]

        return jsonify({"growth": formatted_data}), HTTP_OK
        
    except Exception as e:
        logger.error(f"Erro ao buscar crescimento de usuários: {e}")
        return jsonify({"error": "Erro ao buscar crescimento de usuários"}), HTTP_INTERNAL_ERROR


@admin_bp.route("/admin/product-ratings", methods=["GET"])
@jwt_required()
@admin_required
def get_product_ratings():
    """
    Retorna distribuição de avaliações de produtos (1-5 estrelas).
    
    Returns:
        200: Lista com contagem por rating
        500: Erro ao buscar dados
    """
    try:
        ratings_data = Review.get_product_ratings_distribution()
        return jsonify({"ratings": ratings_data}), HTTP_OK
        
    except Exception as e:
        logger.error(f"Erro ao buscar notas de produtos: {e}")
        return jsonify({"error": "Erro ao buscar notas de produtos"}), HTTP_INTERNAL_ERROR


# ===================================
# GERENCIAMENTO DE USUÁRIOS
# ===================================

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """
    Lista todos os usuários com suporte a busca.
    
    Query Parameters:
        search (str): Termo de busca (nome, username ou email)
    
    Returns:
        200: Lista de usuários
        500: Erro ao buscar usuários
    """
    try:
        search = request.args.get('search', '', type=str).strip()
        query = User.query

        if search:
            like_pattern = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(User.name).like(like_pattern),
                    func.lower(User.username).like(like_pattern),
                    func.lower(User.email).like(like_pattern),
                )
            )

        users = query.all()
        users_data = [user.to_dict(include_sensitive=True) for user in users]

        logger.info(f"Rota /admin/users | search='{search}' | resultados={len(users_data)}")
        return jsonify({"users": users_data}), HTTP_OK

    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return jsonify({"error": "Erro ao buscar usuários"}), HTTP_INTERNAL_ERROR


@admin_bp.route('/admin/users', methods=['POST', 'OPTIONS'])
@jwt_required()
@admin_required
def create_admin_user():
    """
    Cria um novo usuário administrador.
    
    Request Body:
        username (str): Nome de usuário
        email (str): Email
        password (str): Senha
        name (str): Nome completo
    
    Returns:
        201: Admin criado com sucesso
        400: Erro de validação
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json()
    
    user, error = AuthService.create_admin_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        name=data.get('name')
    )
    
    if error:
        return jsonify({'error': error}), HTTP_BAD_REQUEST

    return jsonify({
        'message': 'Administrador criado com sucesso!',
        'user': user.to_dict(include_sensitive=True)
    }), HTTP_CREATED


@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def delete_user_by_admin(user_id):
    """
    Exclui um usuário (admin não pode excluir a si mesmo).
    
    Path Parameters:
        user_id (int): ID do usuário a ser excluído
    
    Returns:
        200: Usuário excluído com sucesso
        403: Tentativa de excluir a si mesmo
        404: Usuário não encontrado
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    admin_user_id = get_jwt_identity()

    if str(admin_user_id) == str(user_id):
        return jsonify({
            "error": ERROR_MESSAGES['CANNOT_DELETE_SELF']
        }), HTTP_FORBIDDEN

    success, error = AuthService.delete_user(user_id, is_self_delete=False)
    
    if error:
        status_code = HTTP_NOT_FOUND if 'não encontrado' in error else HTTP_INTERNAL_ERROR
        return jsonify({"error": error}), status_code
    
    return jsonify({"message": SUCCESS_MESSAGES['USER_DELETED']}), HTTP_OK


@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT', 'OPTIONS'])
@jwt_required()
@admin_required
def update_user_status(user_id):
    """
    Ativa ou inativa um usuário.
    
    Path Parameters:
        user_id (int): ID do usuário
    
    Request Body:
        is_active (bool): True para ativar, False para inativar
    
    Returns:
        200: Status atualizado com sucesso
        400: Campo obrigatório faltando
        403: Tentativa de alterar próprio status
        404: Usuário não encontrado
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    admin_user_id = get_jwt_identity()

    if str(admin_user_id) == str(user_id):
        return jsonify({
            "error": ERROR_MESSAGES['CANNOT_MODIFY_SELF_STATUS']
        }), HTTP_FORBIDDEN

    data = request.get_json() or {}
    
    if "is_active" not in data:
        return jsonify({
            "error": "Campo 'is_active' é obrigatório (true/false)."
        }), HTTP_BAD_REQUEST

    user, error = AuthService.update_user_status(user_id, data["is_active"])
    
    if error:
        return jsonify({"error": error}), HTTP_NOT_FOUND

    status_txt = "ativado" if user.is_active else "inativado"
    return jsonify({
        "message": f"Usuário {status_txt} com sucesso.",
        "user": user.to_dict(include_sensitive=True)
    }), HTTP_OK


# ===================================
# GERENCIAMENTO DE DICAS (TIPS)
# ===================================

@admin_bp.route('/admin/tips', methods=['POST', 'OPTIONS'])
@jwt_required()
@master_admin_required
def create_tip():
    """
    Cria uma nova dica (apenas master admin).
    
    Request Body:
        title (str): Título da dica
        content (str): Conteúdo
        category (str): Categoria
    
    Returns:
        201: Dica criada com sucesso
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json()
    
    new_tip = Tip(
        title=data.get('title'),
        content=data.get('content'),
        category=data.get('category')
    )
    db.session.add(new_tip)
    db.session.commit()

    return jsonify({
        'message': 'Dica criada com sucesso',
        'tip': new_tip.to_dict()
    }), HTTP_CREATED


@admin_bp.route('/admin/tips/<int:tip_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
@master_admin_required
def update_tip(tip_id):
    """
    Atualiza uma dica existente (apenas master admin).
    
    Path Parameters:
        tip_id (int): ID da dica
    
    Request Body:
        Campos a serem atualizados (title, content, category)
    
    Returns:
        200: Dica atualizada com sucesso
        404: Dica não encontrada
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json() or {}
    tip = Tip.query.get_or_404(tip_id)

    if 'title' in data:
        tip.title = data['title']
    if 'content' in data:
        tip.content = data['content']
    if 'category' in data:
        tip.category = data['category']

    db.session.commit()
    return jsonify({"msg": "Dica atualizada com sucesso!"}), HTTP_OK


@admin_bp.route('/admin/tips/<int:tip_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
@master_admin_required
def delete_tip(tip_id):
    """
    Exclui uma dica (apenas master admin).
    
    Path Parameters:
        tip_id (int): ID da dica
    
    Returns:
        200: Dica excluída com sucesso
        404: Dica não encontrada
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    
    return jsonify({"msg": "Dica excluída com sucesso!"}), HTTP_OK


# ===================================
# GERENCIAMENTO DE FAQs
# ===================================

@admin_bp.route('/admin/faqs', methods=['POST', 'OPTIONS'])
@jwt_required()
@master_admin_required
def create_faq():
    """
    Cria uma nova FAQ (apenas master admin).
    
    Request Body:
        question (str): Pergunta
        answer (str): Resposta
    
    Returns:
        201: FAQ criada com sucesso
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json()
    
    new_faq = FAQ(
        question=data.get('question'),
        answer=data.get('answer')
    )
    db.session.add(new_faq)
    db.session.commit()

    return jsonify({
        'message': 'FAQ criada com sucesso',
        'faq': new_faq.to_dict()
    }), HTTP_CREATED


@admin_bp.route('/admin/faqs/<int:faq_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
@master_admin_required
def update_faq(faq_id):
    """
    Atualiza uma FAQ existente (apenas master admin).
    
    Path Parameters:
        faq_id (int): ID da FAQ
    
    Request Body:
        Campos a serem atualizados (question, answer)
    
    Returns:
        200: FAQ atualizada com sucesso
        404: FAQ não encontrada
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json() or {}
    faq = FAQ.query.get_or_404(faq_id)

    if 'question' in data:
        faq.question = data['question']
    if 'answer' in data:
        faq.answer = data['answer']

    db.session.commit()
    return jsonify({"msg": "FAQ atualizada com sucesso!"}), HTTP_OK


@admin_bp.route('/admin/faqs/<int:faq_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
@master_admin_required
def delete_faq(faq_id):
    """
    Exclui uma FAQ (apenas master admin).
    
    Path Parameters:
        faq_id (int): ID da FAQ
    
    Returns:
        200: FAQ excluída com sucesso
        404: FAQ não encontrada
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    
    return jsonify({"msg": "FAQ excluída com sucesso!"}), HTTP_OK


# ===================================
# GERENCIAMENTO DE REDES SOCIAIS
# ===================================

@admin_bp.route('/admin/social-media', methods=['POST', 'OPTIONS'])
@jwt_required()
@admin_required
def create_social_media():
    """
    Adiciona uma rede social.
    
    Request Body:
        platform (str): Nome da plataforma
        url (str): URL do perfil
    
    Returns:
        201: Rede social adicionada com sucesso
        400: Campos obrigatórios faltando
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json()
    platform = data.get('platform')
    url = data.get('url')

    if not platform or not url:
        return jsonify({'error': 'platform e url são obrigatórios'}), HTTP_BAD_REQUEST

    new_social = SocialMedia(platform=platform, url=url)
    db.session.add(new_social)
    db.session.commit()

    return jsonify({
        'message': 'Rede social adicionada com sucesso',
        'social_media': new_social.to_dict()
    }), HTTP_CREATED


@admin_bp.route('/admin/social-media/<int:social_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
@admin_required
def update_social_media(social_id):
    """
    Atualiza uma rede social.
    
    Path Parameters:
        social_id (int): ID da rede social
    
    Request Body:
        Campos a serem atualizados (platform, url)
    
    Returns:
        200: Rede social atualizada com sucesso
        404: Rede social não encontrada
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    data = request.get_json() or {}
    social = SocialMedia.query.get_or_404(social_id)

    if 'platform' in data:
        social.platform = data['platform']
    if 'url' in data:
        social.url = data['url']

    db.session.commit()
    return jsonify({"msg": "Rede social atualizada com sucesso!"}), HTTP_OK


@admin_bp.route('/admin/social-media/<int:social_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def delete_social_media(social_id):
    """
    Exclui uma rede social.
    
    Path Parameters:
        social_id (int): ID da rede social
    
    Returns:
        200: Rede social excluída com sucesso
        404: Rede social não encontrada
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK

    social = SocialMedia.query.get_or_404(social_id)
    db.session.delete(social)
    db.session.commit()
    
    return jsonify({"msg": "Rede social excluída com sucesso!"}), HTTP_OK
