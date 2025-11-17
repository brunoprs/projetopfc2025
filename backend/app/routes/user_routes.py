"""
Rotas de gerenciamento de conta do usuário.

Este módulo contém endpoints para o usuário gerenciar sua própria conta.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from ..services import AuthService
from ..constants import (
    ALLOWED_ORIGINS,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    HTTP_OK,
    HTTP_NOT_FOUND,
    HTTP_BAD_REQUEST
)

user_bp = Blueprint("user", __name__)
CORS(user_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


@user_bp.route("/user/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Retorna dados do usuário logado.
    
    Returns:
        200: Dados do usuário
        404: Usuário não encontrado
    """
    from ..models import User
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": ERROR_MESSAGES['USER_NOT_FOUND']}), HTTP_NOT_FOUND
    
    return jsonify(user.to_dict(include_sensitive=True)), HTTP_OK


@user_bp.route("/user/update", methods=["PUT"])
@jwt_required()
def update_user():
    """
    Atualiza dados do usuário logado.
    
    Request Body:
        name (str): Nome completo (opcional)
        username (str): Nome de usuário (opcional)
        email (str): Email (opcional)
    
    Returns:
        200: Usuário atualizado com sucesso
        404: Usuário não encontrado
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user, error = AuthService.update_user(user_id, **data)
    
    if error:
        return jsonify({"error": error}), HTTP_NOT_FOUND
    
    return jsonify({"message": SUCCESS_MESSAGES['USER_UPDATED']}), HTTP_OK


@user_bp.route("/user/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """
    Altera a senha do usuário logado.
    
    Request Body:
        current_password (str): Senha atual
        new_password (str): Nova senha
    
    Returns:
        200: Senha alterada com sucesso
        400: Validação falhou
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    success, error = AuthService.change_password(
        user_id=user_id,
        current_password=data.get("current_password"),
        new_password=data.get("new_password")
    )
    
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST
    
    return jsonify({"message": SUCCESS_MESSAGES['PASSWORD_CHANGED']}), HTTP_OK


@user_bp.route("/user/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """
    Exclui a conta do usuário logado.
    
    Returns:
        200: Conta excluída com sucesso
        403: Admin não pode excluir por esta rota
    """
    user_id = get_jwt_identity()
    
    success, error = AuthService.delete_user(user_id, is_self_delete=True)
    
    if error:
        return jsonify({"error": error}), HTTP_BAD_REQUEST
    
    return jsonify({"message": SUCCESS_MESSAGES['USER_DELETED']}), HTTP_OK
