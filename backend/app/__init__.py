from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from sqlalchemy import text

# Carrega .env
load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, static_folder='static')

    # ==============================
    # Configurações principais
    # ==============================
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///:memory:"  # fallback seguro para testes
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv(
        "JWT_SECRET_KEY",
        "chave-de-teste"
    )

    # Se testes quiserem sobrescrever config
    if test_config:
        app.config.update(test_config)

    # ==============================
    # Inicialização das extensões
    # ==============================
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # ==============================
    # CORS
    # ==============================
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"]
    )

    # ==============================
    # JWT
    # ==============================
    jwt = JWTManager(app)

    from .models import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(int(identity))

    # ==============================
    # Teste de conexão com banco
    # ==============================
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("Conexão com o banco OK!")
        except Exception as e:
            print("ERRO AO CONECTAR NO BANCO:")
            print(e)

    # ==============================
    # Blueprints
    # ==============================
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    print("🚀 Flask app iniciado (create_app).")
    return app
