"""
Módulo de serviços da aplicação.

Este módulo exporta todos os serviços disponíveis para facilitar importação.
"""
from .product_service import ProductService
from .auth_service import AuthService
from .chatbot_service import ChatbotService, chatbot_service

__all__ = [
    'ProductService',
    'AuthService',
    'ChatbotService',
    'chatbot_service',
]
