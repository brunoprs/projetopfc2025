import pytest
from datetime import datetime
from unittest.mock import Mock

from app.models import Product, Favorite
from app.utils.banned_words import contains_banned_word


# ============================================================
# 1 — MÉDIA DE NOTAS
# ============================================================

def test_calcular_media_rating_pura():
    notas = [5, 4, 5]
    media = round(sum(notas) / len(notas), 1)
    assert media == 4.7

    notas = [5, None, 4, 5]
    valores = [n for n in notas if n is not None]
    media = round(sum(valores) / len(valores), 1)
    assert media == 4.7

    notas = []
    valores = [n for n in notas if n is not None]
    assert valores == []
    assert len(valores) == 0


# ============================================================
# 2 — VALIDAÇÃO DE RATING (1 A 5)
# ============================================================

def test_rating_valido():
    def rating_valido(r):
        return r is not None and 1 <= r <= 5

    assert rating_valido(1) is True
    assert rating_valido(5) is True
    assert rating_valido(3) is True
    assert rating_valido(0) is False
    assert rating_valido(6) is False
    assert rating_valido(None) is False


# ============================================================
# 3 — SENHA CADASTRÁVEL 
# ============================================================

def test_senha_cadastravel():
    def senha_valida_para_cadastro(s: str) -> bool:

        if s is None:
            return False
        return len(s) >= 6


    assert senha_valida_para_cadastro("senha123") is True
    assert senha_valida_para_cadastro("senhagrande123") is True
    assert senha_valida_para_cadastro("senhagigantesca1234") is True


    assert senha_valida_para_cadastro("123") is False
    assert senha_valida_para_cadastro("") is False
    assert senha_valida_para_cadastro("     ") is False
    assert senha_valida_para_cadastro(None) is False


# ============================================================
# 4 — CRESCIMENTO DE USUÁRIOS
# ============================================================

def test_crescimento_usuarios_puro():
    usuarios = [
        Mock(created_at=datetime(2025, 1, 10)),
        Mock(created_at=datetime(2025, 1, 28)),
        Mock(created_at=datetime(2025, 2, 5)),
        Mock(created_at=datetime(2025, 1, 1)),
    ]
    crescimento = {}
    for u in usuarios:
        key = f"{u.created_at.year}-{u.created_at.month:02d}"
        crescimento[key] = crescimento.get(key, 0) + 1

    assert crescimento["2025-01"] == 3
    assert crescimento["2025-02"] == 1
    assert "2025-03" not in crescimento


# ============================================================
# 5 — PRODUTO MAIS BARATO
# ============================================================

def test_produto_mais_barato_puro():
    produtos = [
        {"name": "Caro", "price": 200.0},
        {"name": "Barato", "price": 50.0},
        {"name": "Médio", "price": 120.0},
    ]
    mais_barato = min(produtos, key=lambda p: p["price"])
    assert mais_barato["name"] == "Barato"
    assert mais_barato["price"] == 50.0


# ============================================================
# 6 — FILTRO POR TIPO (LAMINADO)
# ============================================================

def test_filtro_tipo_laminado():
    produtos = [
        {"type": "Laminado"},
        {"type": "vinílico"},
        {"type": "LAMINADO TOP"},
        {"type": "porcelanato"},
    ]
    resultado = [p for p in produtos if "laminado" in p["type"].lower()]
    assert len(resultado) == 2
    assert all("laminado" in p["type"].lower() for p in resultado)


# ============================================================
# 7 — PAGINAÇÃO (CÁLCULO DE PÁGINAS)
# ============================================================

def test_paginacao_calculo_paginas():
    def paginas(total, por_pagina):
        return (total + por_pagina - 1) // por_pagina

    assert paginas(47, 10) == 5
    assert paginas(50, 10) == 5
    assert paginas(51, 10) == 6
    assert paginas(0, 10) == 0


# ============================================================
# 8 — PERMISSÃO PARA DELETAR REVIEW (DONO OU ADMIN)
# ============================================================

def test_pode_deletar_review():
    def pode_deletar(review_user_id: int, current_user_id: int, is_admin: bool) -> bool:
        return review_user_id == current_user_id or is_admin

    assert pode_deletar(10, 10, False) is True   # dono
    assert pode_deletar(10, 99, True) is True    # admin
    assert pode_deletar(10, 88, False) is False  # outro usuário


# ============================================================
# 9 — FAVORITOS: TOGGLE E REMOÇÃO DE DUPLICATAS
# ============================================================

def test_toggle_favoritos_puro():
    favoritos = [1, 2, 3]
    pid = 99

    if pid not in favoritos:
        favoritos.append(pid)
    assert 99 in favoritos

    favoritos = [f for f in favoritos if f != pid]
    assert 99 not in favoritos


def test_remove_duplicatas_favoritos():
    favs = [1, 2, 2, 3, 1, 4]
    unicos = list(dict.fromkeys(favs))
    assert unicos == [1, 2, 3, 4]


# ============================================================
# 10 — CONTAGEM DE FAVORITOS POR PRODUTO
# ============================================================

def test_conta_favoritos_por_produto():
    usuarios = [
        Mock(favorites=[1, 2]),
        Mock(favorites=[1, 3]),
        Mock(favorites=[2]),
    ]
    contagem = {}
    for u in usuarios:
        for pid in u.favorites:
            contagem[pid] = contagem.get(pid, 0) + 1

    assert contagem[1] == 2
    assert contagem[2] == 2
    assert contagem[3] == 1


# ============================================================
# 11 — CAMPOS OBRIGATÓRIOS (create_user, create_product, etc.)
# ============================================================

def test_validacao_campos_obrigatorios():
    def valida(dados: dict, campos: list[str]):
        for c in campos:
            if c not in dados or not dados[c]:
                raise ValueError(f"{c} é obrigatório")

    valida({"username": "joao", "email": "j@test.com"}, ["username", "email"])

    with pytest.raises(ValueError, match="email é obrigatório"):
        valida({"username": "joao"}, ["username", "email"])


# ============================================================
# 12 — EMAIL EM LOWERCASE (login, create_user)
# ============================================================

def test_email_salvo_em_lowercase():
    email = "USUARIO@GMAIL.COM"
    email_lower = email.lower()
    assert email_lower == "usuario@gmail.com"
    assert email_lower.islower()


# ============================================================
# 13 — BUSCA CASE INSENSITIVE (nome/tipo/brand)
# ============================================================

def test_busca_case_insensitive():
    produto = {"name": "Piso LAMINADO Top", "type": "LAMINADO", "brand": "Durafloor"}
    termo = "laminado"
    campos = ["name", "type", "brand"]
    assert any(termo.lower() in produto[c].lower() for c in campos)
    assert "vinílico" not in produto["name"].lower()


# ============================================================
# 14 — CONTAINS_BANNED_WORD
# ============================================================

def test_contains_banned_word_true():
    assert contains_banned_word("Que merda de piso é esse?") is True


def test_contains_banned_word_false():
    assert contains_banned_word("Comentário limpo e educado") is False


def test_contains_banned_word_vazio_ou_none():
    assert contains_banned_word("") is False
    assert contains_banned_word(None) is False


# ============================================================
# 15 — CENSURA MANUAL DE PALAVRAS
# ============================================================

def test_censura_palavras_pura():
    proibidas = ["merda", "porra", "caralho"]
    texto1 = "que merda é essa"
    texto2 = "tudo ótimo por aqui"

    assert any(p in texto1.lower() for p in proibidas) is True
    assert any(p in texto2.lower() for p in proibidas) is False


# ============================================================
# 16 — UPDATE PARCIAL DE PRODUTO EM MEMÓRIA
# ============================================================

def test_update_parcial_produto_em_memoria():
    produto = Product(
        name="Piso Antigo",
        price=100.0,
        type="laminado",
        description="desc",
        image_url="img",
        video_url="vid",
    )
    dados = {"name": "Piso Novo", "price": 150.0}

    if "name" in dados:
        produto.name = dados["name"]
    if "price" in dados:
        produto.price = dados["price"]

    assert produto.name == "Piso Novo"
    assert produto.price == 150.0
    assert produto.type == "laminado"
