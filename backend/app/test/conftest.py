# app/test/conftest.py
import os
import pytest

# Isola os testes no SQLite em memória 
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
os.environ.setdefault("JWT_SECRET_KEY", "jwt-test-secret")

from app import create_app, db, bcrypt
from flask_jwt_extended import create_access_token
from sqlalchemy import event
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope="session")
def app():
    """Cria o app de teste com tabelas em memória."""
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        db.create_all()
    yield app
    # memória: nada a limpar

@pytest.fixture(autouse=True)
def _push_app_ctx(app):
    """Mantém um application context ativo durante cada teste."""
    ctx = app.app_context()
    ctx.push()
    try:
        yield
    finally:
        ctx.pop()

@pytest.fixture(autouse=True)
def db_session(app):
    """
    Transação + savepoint por teste, usando a API do SQLAlchemy 2.0/Flask-SQLAlchemy 3.x.
    Substitui db.session por um scoped_session ligado à conexão transacionada.
    """
    # 1) abre conexão e transação de nível superior
    connection = db.engine.connect()
    transaction = connection.begin()

    # 2) cria uma sessão ligada à connection
    Session = sessionmaker(bind=connection, autoflush=False, autocommit=False, expire_on_commit=False)
    session = scoped_session(Session)

    # 3) troca o db.session da app pela sessão de teste
    old_session = db.session
    db.session = session

    # 4) savepoint por teste
    nested = connection.begin_nested()

    @event.listens_for(session(), "after_transaction_end")
    def restart_savepoint(sess, trans_ended):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        # 5) rollback total e limpeza
        session.remove()
        transaction.rollback()
        connection.close()
        db.session = old_session

@pytest.fixture()
def client(app):
    return app.test_client()

# -------------------- Helpers --------------------

@pytest.fixture()
def make_user():
    """Cria e persiste um usuário comum ou admin."""
    from app.models import User
    def _make(
        username="user",
        email="user@example.com",
        password="123456",
        name="Usuário",
        is_admin=False,
    ):
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        u = User(
            username=username,
            email=email.lower(),
            password_hash=pw_hash,
            name=name,
            is_admin=is_admin,
        )
        db.session.add(u)
        db.session.commit()
        return u
    return _make

@pytest.fixture()
def make_token(app):
    """Gera um Bearer JWT (identity=string, conforme sua app)."""
    from flask_jwt_extended import create_access_token

    def _make(user_id, **claims):
        with app.app_context():
            # ✅ identity como string (seu /login faz str(user.id))
            token = create_access_token(identity=str(user_id), additional_claims=claims)
        return f"Bearer {token}"
    return _make

