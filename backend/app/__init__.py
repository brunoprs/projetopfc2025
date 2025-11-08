from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static')

    # ==============================
    # Configurações principais
    # ==============================
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+mysqlconnector://root:%40Password123@localhost/pisos_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv(
        'JWT_SECRET_KEY',
        '31f43bd2635de949e80f6cbbf14c9f9c06470d8bbb23453900001ed9707cbb96'
    )

    # ==============================
    # Inicialização das extensões
    # ==============================
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # ✅ Configuração única e correta do CORS
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
    # Blueprints
    # ==============================
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    print("✅ Flask app rodando com CORS liberado para http://localhost:5173")

    return app
