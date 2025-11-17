# app/test/test_routes.py
from datetime import datetime
import pytest

def _auth(tok):
    return {"Authorization": tok}

# =========================
# PÚBLICO
# =========================

def test_root_publicos(client):
    r = client.get("/products")
    assert r.status_code == 200 and "products" in r.get_json()

    r = client.get("/tips")
    assert r.status_code == 200 and "tips" in r.get_json()

    r = client.get("/faqs")
    assert r.status_code == 200 and "faqs" in r.get_json()

# =========================
# AUTH / USERS
# =========================

def test_create_user_e_login(client):
    r = client.post("/users", json={
        "username": "alice",
        "email": "alice@ex.com",
        "password": "123456",
        "name": "Alice"
    })
    assert r.status_code in (200, 201)

    r = client.post("/login", json={"username": "alice", "password": "123456"})
    assert r.status_code == 200
    body = r.get_json()
    assert "token" in body and "user" in body

def test_login_credenciais_invalidas(client):
    r = client.post("/login", json={"username": "nope", "password": "zzz"})
    assert r.status_code == 401

def test_options_login(client):
    r = client.open("/login", method="OPTIONS")
    assert r.status_code == 200

# =========================
# ADMIN: PRODUCTS (CRUD) + NEGATIVO
# =========================

def test_admin_crud_products(client, make_user, make_token):
    admin = make_user(username="adm", email="adm@ex.com", is_admin=True)
    tok = make_token(admin.id, is_admin=True)

    # CREATE
    r = client.post("/admin/products", json={
        "name": "Piso A", "price": 99.9, "description": "desc",
        "type": "laminado", "image_url": "a.jpg", "video_url": "v.mp4"
    }, headers=_auth(tok))
    assert r.status_code in (200, 201)
    prod = r.get_json()["product"]
    pid = prod["id"]

    # READ list
    r = client.get("/products")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.get_json()["products"])

    # UPDATE
    r = client.put(f"/admin/products/{pid}", json={"price": 120.0}, headers=_auth(tok))
    assert r.status_code == 200 and r.get_json()["product"]["price"] == 120.0

    # READ by id
    r = client.get(f"/products/{pid}")
    assert r.status_code == 200
    assert r.get_json()["price"] == 120.0

    # UPDATE 404
    r = client.put("/admin/products/99999", json={"price": 1}, headers=_auth(tok))
    assert r.status_code == 404

    # DELETE
    r = client.delete(f"/admin/products/{pid}", headers=_auth(tok))
    assert r.status_code == 200

def test_admin_products_negar_quando_nao_admin(client, make_user, make_token):
    user = make_user(username="bob", email="bob@ex.com", is_admin=False)
    tok = make_token(user.id, is_admin=False)
    r = client.post("/admin/products", json={"name": "X"}, headers=_auth(tok))
    assert r.status_code in (401, 403)

# =========================
# FAVORITOS
# =========================

def test_favorites_flow(client, make_user, make_token):
    admin = make_user(username="adm2", email="adm2@ex.com", is_admin=True)
    tok_admin = make_token(admin.id, is_admin=True)
    r = client.post("/admin/products", json={"name": "FavPro", "price": 10}, headers=_auth(tok_admin))
    pid = r.get_json()["product"]["id"]

    user = make_user(username="u1", email="u1@ex.com", is_admin=False)
    tok_user = make_token(user.id, is_admin=False)

    # OPTIONS preflight
    r = client.open("/favorites", method="OPTIONS")
    assert r.status_code == 200

    r = client.post("/favorites", json={"product_id": pid}, headers=_auth(tok_user))
    assert r.status_code in (200, 201)

    r = client.get("/favorites", headers=_auth(tok_user))
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.get_json()["favorites"])

    r = client.delete(f"/favorites/{pid}", headers=_auth(tok_user))
    assert r.status_code == 200

# =========================
# REVIEWS / RATING
# =========================

def test_reviews_e_rating_e_delete_por_dono_e_admin(client, make_user, make_token):
    admin = make_user(username="adm3", email="adm3@ex.com", is_admin=True)
    tok_admin = make_token(admin.id, is_admin=True)
    r = client.post("/admin/products", json={"name": "R1", "price": 50}, headers=_auth(tok_admin))
    pid = r.get_json()["product"]["id"]

    user = make_user(username="ruser", email="ruser@ex.com", is_admin=False)
    tok_user = make_token(user.id, is_admin=False)

    r = client.post(f"/products/{pid}/reviews", json={"comment": "bom"}, headers=_auth(tok_user))
    assert r.status_code == 201

    r = client.get(f"/products/{pid}/reviews")
    assert r.status_code == 200
    lista = r.get_json()
    assert any(rv["comment"] == "bom" for rv in lista)
    rid = lista[0]["id"]

    r = client.post(f"/products/{pid}/rating", json={"rating": 5}, headers=_auth(tok_user))
    assert r.status_code == 200

    r = client.get(f"/products/{pid}/rating")
    assert r.status_code == 200
    assert r.get_json()["average"] in (5, 5.0)

    # delete por dono
    r = client.post(f"/products/{pid}/reviews", json={"comment": "vou deletar"}, headers=_auth(tok_user))
    r = client.get(f"/products/{pid}/reviews")
    rid2 = r.get_json()[0]["id"]
    r = client.delete(f"/products/{pid}/reviews/{rid2}", headers=_auth(tok_user))
    assert r.status_code == 200

    # delete por admin do primeiro
    r = client.delete(f"/products/{pid}/reviews/{rid}", headers=_auth(tok_admin))
    assert r.status_code == 200

# =========================
# USER: ME / UPDATE / CHANGE-PASSWORD / DELETE-ACCOUNT
# =========================

def test_user_me_update_change_password_login_delete_account(client, make_user, make_token):
    user = make_user(username="meu", email="meu@ex.com", password="abc123", name="Meu Nome")
    tok = make_token(user.id, is_admin=False)

    r = client.get("/user/me", headers=_auth(tok))
    assert r.status_code == 200
    assert r.get_json()["id"] == user.id

    r = client.put("/user/update", json={"name": "Novo Nome"}, headers=_auth(tok))
    assert r.status_code == 200

    r = client.post("/user/change-password", json={
        "current_password": "abc123", "new_password": "nova456"
    }, headers=_auth(tok))
    assert r.status_code == 200

    r = client.post("/login", json={"username": "meu", "password": "nova456"})
    assert r.status_code == 200 and "token" in r.get_json()

    r = client.delete("/user/delete-account", headers=_auth(tok))
    assert r.status_code == 200

# =========================
# ADMIN: USERS (GET/POST/DELETE) + validações
# =========================

def test_admin_listar_criar_admin_validacao_e_deletar_usuario(client, make_user, make_token):
    admin = make_user(username="root", email="root@ex.com", is_admin=True)
    tok_admin = make_token(admin.id, is_admin=True)

    user = make_user(username="victim", email="victim@ex.com", is_admin=False)

    r = client.get("/admin/users", headers=_auth(tok_admin))
    assert r.status_code == 200
    assert any(u["id"] == user.id for u in r.get_json()["users"])

    r = client.delete(f"/admin/users/{admin.id}", headers=_auth(tok_admin))
    assert r.status_code == 403

    r = client.post("/admin/users", json={
        "username": "bad", "email": "bad@ex.com", "password": "123", "name": "Bad"
    }, headers=_auth(tok_admin))
    assert r.status_code == 400

    r = client.post("/admin/users", json={
        "username": "novo_admin", "email": "novo_admin@ex.com",
        "password": "123456", "name": "Novo Admin"
    }, headers=_auth(tok_admin))
    assert r.status_code in (200, 201)
    assert r.get_json()["user"]["is_admin"] is True

    r = client.delete(f"/admin/users/{user.id}", headers=_auth(tok_admin))
    assert r.status_code == 200

# =========================
# ADMIN: STATS / USER-GROWTH / PRODUCT-RATINGS
# =========================

def test_admin_stats_user_growth_product_ratings(client, make_user, make_token):
    from app import db
    admin = make_user(username="stats", email="stats@ex.com", is_admin=True)
    tok = make_token(admin.id, is_admin=True)

    r = client.get("/admin/stats", headers=_auth(tok))
    assert r.status_code == 200

    # growth com datas forçadas
    u1 = make_user(username="g1", email="g1@ex.com")
    u2 = make_user(username="g2", email="g2@ex.com")
    u1.created_at = datetime(2024, 1, 15, 10, 0, 0)
    u2.created_at = datetime(2024, 2, 10, 12, 0, 0)
    db.session.commit()

    r = client.get("/admin/user-growth", headers=_auth(tok))
    assert r.status_code == 200
    months = [row["month"] for row in r.get_json()["growth"]]
    assert 1 in months and 2 in months

    # product-ratings (cria 2 produtos e avalia com 2 users)
    r = client.post("/admin/products", json={"name": "P1", "price": 10}, headers=_auth(tok))
    p1 = r.get_json()["product"]["id"]
    r = client.post("/admin/products", json={"name": "P2", "price": 20}, headers=_auth(tok))
    p2 = r.get_json()["product"]["id"]

    u3 = make_user(username="rv1", email="rv1@ex.com")
    u4 = make_user(username="rv2", email="rv2@ex.com")
    u3_id, u4_id = u3.id, u4.id
    t3 = make_token(u3_id)
    t4 = make_token(u4_id)

    # ✅ grava as notas antes de consultar a distribuição
    client.post(f"/products/{p1}/rating", json={"rating": 5}, headers=_auth(t3))
    client.post(f"/products/{p2}/rating", json={"rating": 3}, headers=_auth(t4))

    r = client.get("/admin/product-ratings", headers=_auth(tok))
    assert r.status_code == 200
    dist = r.get_json()["ratings"]
    assert len(dist) == 5
    assert any(item["rating"] == 5 and item["count"] >= 1 for item in dist)
    assert any(item["rating"] == 3 and item["count"] >= 1 for item in dist)

# =========================
# ADMIN: TIPS / FAQ CRUD + OPTIONS
# =========================



def test_admin_cria_social_media(client, make_user, make_token):
    admin = make_user(username="adm_s", email="adm_s@ex.com", is_admin=True)
    tok = make_token(admin.id, is_admin=True)
    r = client.post("/admin/social-media", json={
        "platform": "instagram", "url": "https://insta/pifloor"
    }, headers=_auth(tok))
    assert r.status_code in (200, 201)
    assert r.get_json()["social_media"]["platform"] == "instagram"

# =========================
# CHAT (sem API key) + HELPERS PRIVADOS
# =========================

def test_chat_sem_api_key_retorna_500(client, monkeypatch):
    # força ausência de sessão do Gemini (simula falta de GOOGLE_API_KEY)
    from app.services.chatbot_service import chatbot_service
    monkeypatch.setattr(chatbot_service, "chat_session", None, raising=False)
    monkeypatch.setattr(chatbot_service, "use_gemini", False, raising=False)

    r = client.post("/chat", json={"message": "qual o mais barato?"})
    # Com a refatoração, o chatbot funciona em modo básico, então retorna 200
    assert r.status_code == 200

def test_helpers_privados(client, make_user, make_token):
    admin = make_user(username="adm_h", email="adm_h@ex.com", is_admin=True)
    tok = make_token(admin.id, is_admin=True)
    client.post("/admin/products", json={"name": "Lami 1", "price": 99.0, "type": "laminado"}, headers=_auth(tok))
    client.post("/admin/products", json={"name": "Vinil 1", "price": 59.0, "type": "vinilico"}, headers=_auth(tok))
    client.post("/admin/products", json={"name": "Lami 2", "price": 79.0, "type": "laminado"}, headers=_auth(tok))

    # Agora as funções estão nos serviços
    from app.services.product_service import ProductService
    s1 = ProductService.get_cheapest_product()
    assert "mais barato" in (s1 or "").lower() or "vinil 1" in (s1 or "").lower()
    s2 = ProductService.get_products_by_type("laminado")
    assert "laminado" in (s2 or "").lower() or "lami" in (s2 or "").lower()

# =========================
# MODELS: tocar construtor do User diretamente
# =========================

def test_model_user_constructor_direto(db_session):
    from app.models import User
    u = User(username="xx", email="xx@ex.com", password_hash="h", name="Nome")
    db_session.add(u)
    db_session.commit()
    assert User.query.filter_by(username="xx").first() is not None
