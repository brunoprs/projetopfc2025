"""
Rotas do chatbot com IA.

Este módulo contém endpoints relacionados ao chatbot.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from ..services import chatbot_service
from ..constants import (
    ALLOWED_ORIGINS,
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_ERROR
)

chat_bp = Blueprint("chat", __name__)
CORS(chat_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


@chat_bp.route('/chat', methods=['POST'])
@jwt_required(optional=True)
def handle_chat():
    """
    Processa mensagem do usuário e retorna resposta do chatbot.
    
    Request Body:
        message (str): Mensagem do usuário
    
    Returns:
        200: Resposta do chatbot
        400: Mensagem não fornecida
        500: Erro no serviço de IA
    """
    if not chatbot_service.is_available():
        return jsonify({
            "error": "Desculpe, o serviço de IA não está configurado."
        }), HTTP_INTERNAL_ERROR
    
    data = request.get_json()
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"error": "Mensagem não fornecida."}), HTTP_BAD_REQUEST
    
    reply, error = chatbot_service.send_message(user_message)
    
    if error:
        return jsonify({"error": error}), HTTP_INTERNAL_ERROR
    
    return jsonify({"reply": reply}), HTTP_OK
