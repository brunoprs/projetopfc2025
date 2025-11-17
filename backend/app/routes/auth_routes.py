"""
Rotas de autenticação (login, registro, logout).

Este módulo contém endpoints relacionados à autenticação de usuários.
"""
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from ..services import AuthService
from ..constants import (
    ALLOWED_ORIGINS,
    SUCCESS_MESSAGES,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN
)

auth_bp = Blueprint("auth", __name__)
CORS(auth_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


@auth_bp.route('/users', methods=['POST'])
def register():
    """
    Registra um novo usuário no sistema.
    
    Request Body:
        username (str): Nome de usuário
        email (str): Email do usuário
        password (str): Senha
        name (str): Nome completo
    
    Returns:
        201: Usuário criado com sucesso
        400: Erro de validação
    """
    data = request.json
    
    user, error = AuthService.register_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        name=data.get('name')
    )
    
    if error:
        return jsonify({'error': error}), HTTP_BAD_REQUEST
    
    return jsonify({
        'message': SUCCESS_MESSAGES['USER_CREATED'],
        'user': user.to_dict()
    }), HTTP_CREATED


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Autentica um usuário e retorna token JWT.
    
    Request Body:
        username (str): Username ou email
        password (str): Senha
    
    Returns:
        200: Login bem-sucedido com token
        400: Campos obrigatórios faltando
        401: Credenciais inválidas
        403: Conta inativa
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK
    
    data = request.json
    
    token, user, error = AuthService.login_user(
        login_identifier=data.get('username'),
        password=data.get('password')
    )
    
    if error:
        status_code = HTTP_FORBIDDEN if 'inativado' in error else HTTP_UNAUTHORIZED
        return jsonify({'error': error}), status_code
    
    return jsonify({
        'message': SUCCESS_MESSAGES['LOGIN_SUCCESS'],
        'token': token,
        'user': user.to_dict(include_sensitive=True)
    }), HTTP_OK
