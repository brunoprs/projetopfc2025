"""
Decorators personalizados para autenticação e autorização.

Este módulo fornece decorators reutilizáveis para proteger rotas
que requerem permissões específicas (admin, master admin, etc).
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from .constants import ERROR_MESSAGES, HTTP_FORBIDDEN, MASTER_ADMIN_ID


def admin_required(f):
    """
    Decorator que requer que o usuário seja um administrador.
    
    Deve ser usado após @jwt_required() nas rotas.
    
    Usage:
        @bp.route('/admin/endpoint')
        @jwt_required()
        @admin_required
        def admin_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({"error": ERROR_MESSAGES['ACCESS_DENIED_ADMIN']}), HTTP_FORBIDDEN
        
        return f(*args, **kwargs)
    
    return decorated_function


def master_admin_required(f):
    """
    Decorator que requer que o usuário seja o administrador master (ID específico).
    
    Deve ser usado após @jwt_required() nas rotas.
    
    Usage:
        @bp.route('/admin/critical-endpoint')
        @jwt_required()
        @master_admin_required
        def critical_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        
        if str(user_id) != str(MASTER_ADMIN_ID):
            return jsonify({"error": ERROR_MESSAGES['ACCESS_DENIED_MASTER']}), HTTP_FORBIDDEN
        
        return f(*args, **kwargs)
    
    return decorated_function


def active_user_required(f):
    """
    Decorator que requer que o usuário esteja ativo.
    
    Deve ser usado após @jwt_required() nas rotas.
    
    Usage:
        @bp.route('/user/endpoint')
        @jwt_required()
        @active_user_required
        def user_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": ERROR_MESSAGES['USER_NOT_FOUND']}), HTTP_FORBIDDEN
        
        if not user.is_active:
            return jsonify({"error": ERROR_MESSAGES['ACCOUNT_INACTIVE']}), HTTP_FORBIDDEN
        
        return f(*args, **kwargs)
    
    return decorated_function
