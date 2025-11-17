"""
Módulo de rotas da aplicação.

Este módulo exporta todos os blueprints de rotas para facilitar registro.
"""
from .auth_routes import auth_bp
from .product_routes import product_bp
from .user_routes import user_bp
from .chat_routes import chat_bp
from .admin_routes import admin_bp
from .favorite_routes import favorite_bp
from .review_routes import review_bp
from .public_routes import public_bp

__all__ = [
    'auth_bp',
    'product_bp',
    'user_bp',
    'chat_bp',
    'admin_bp',
    'favorite_bp',
    'review_bp',
    'public_bp',
]
