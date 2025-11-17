"""
Inicialização da aplicação Flask.

Este módulo configura e inicializa a aplicação Flask com todas as extensões,
configurações e blueprints necessários.
"""
import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização de extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app():
    """
    Factory function para criar e configurar a aplicação Flask.
    
    Returns:
        Aplicação Flask configurada
    """
    app = Flask(__name__, static_folder='static')
    
    # ==============================
    # Configurações
    # ==============================
    _configure_app(app)
    
    # ==============================
    # Inicialização das extensões
    # ==============================
    _initialize_extensions(app)
    
    # ==============================
    # Configuração de CORS
    # ==============================
    _configure_cors(app)
    
    # ==============================
    # Configuração de JWT
    # ==============================
    _configure_jwt(app)
    
    # ==============================
    # Registro de Blueprints
    # ==============================
    _register_blueprints(app)
    
    # ==============================
    # Rotas básicas
    # ==============================
    _register_basic_routes(app)
    
    logger.info("✅ Flask app inicializada com sucesso")
    
    return app


def _configure_app(app):
    """Configura as variáveis de configuração da aplicação."""
    # Database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+mysqlconnector://root:%40Password123@localhost/pisos_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret:
        logger.warning(
            "⚠️  JWT_SECRET_KEY não configurada! Usando chave padrão (NÃO USE EM PRODUÇÃO)"
        )
        jwt_secret = '31f43bd2635de949e80f6cbbf14c9f9c06470d8bbb23453900001ed9707cbb96'
    
    app.config['JWT_SECRET_KEY'] = jwt_secret


def _initialize_extensions(app):
    """Inicializa as extensões Flask."""
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)


def _configure_cors(app):
    """Configura CORS para permitir requisições do frontend."""
    from .constants import ALLOWED_ORIGINS
    
    CORS(
        app,
        resources={r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }}
    )
    logger.info(f"✅ CORS configurado para: {ALLOWED_ORIGINS}")


def _configure_jwt(app):
    """Configura JWT Manager e callbacks."""
    jwt = JWTManager(app)
    
    from .models import User
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Callback para carregar usuário a partir do token JWT."""
        identity = jwt_data["sub"]
        return User.query.get(int(identity))


def _register_blueprints(app):
    """Registra todos os blueprints de rotas."""
    # Importa blueprints refatorados
    try:
        from .routes import (
            auth_bp, product_bp, user_bp, chat_bp,
            admin_bp, favorite_bp, review_bp, public_bp
        )
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(product_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(chat_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(favorite_bp)
        app.register_blueprint(review_bp)
        app.register_blueprint(public_bp)
        
        logger.info("✅ Todos os blueprints refatorados registrados com sucesso")
    except ImportError as e:
        logger.warning(f"⚠️  Erro ao importar blueprints refatorados: {e}")
        logger.info("Tentando usar routes.py original como fallback...")
        
        # Fallback para routes.py original
        try:
            from .routes_original_backup import bp as routes_bp
            app.register_blueprint(routes_bp)
            logger.info("✅ Blueprint original registrado como fallback")
        except ImportError as e2:
            logger.error(f"❌ Erro ao importar routes original: {e2}")


def _register_basic_routes(app):
    """Registra rotas básicas da aplicação."""
    from flask import jsonify, request
    
    # Handler global para OPTIONS (CORS preflight)
    @app.before_request
    def handle_preflight():
        """Trata requisições OPTIONS (CORS preflight) globalmente."""
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response, 200
    
    @app.route('/')
    def index():
        """Rota raiz da aplicação."""
        return render_template('index.html')
