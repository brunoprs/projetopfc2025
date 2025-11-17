import os
import google.generativeai as genai

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from . import db, bcrypt
from .models import Product, User, Review, Tip, FAQ, Favorite, db
from datetime import datetime
from flask_cors import CORS
from sqlalchemy import func
from sqlalchemy import func, or_

# ===================================
# CONFIGURAÇÃO DO BLUEPRINT E CORS
# ===================================
# Cria um "grupo" de rotas chamado 'routes'
bp = Blueprint("routes", __name__)
# Libera o acesso CORS apenas para o frontend rodando em http://localhost:5173
CORS(bp, supports_credentials=True, origins=["http://localhost:5173"])

# ===================================
# FUNÇÕES AUXILIARES
# ===================================

def admin_required():
    # Recupera o ID do usuário logado (a partir do token JWT)
    user_id = get_jwt_identity()
    # Busca o usuário no banco
    user = User.query.get(user_id)
    # Se não existir ou não for admin, bloqueia o acesso
    if not user or not user.is_admin:
        return jsonify({"msg": "Acesso negado: apenas administradores"}), 403
    # Se for admin, retorna None (libera a rota)
    return None

def admin_7_required():
    # Recupera o ID do usuário logado
    user_id = get_jwt_identity()
    # Só permite acesso se o ID for exatamente 7 (admin "master")
    if str(user_id) != "7":
        return jsonify({"msg": "Acesso negado: apenas o administrador (ID 7)"}), 403
    return None

# ===================================
# ROTAS PÚBLICAS
# ===================================

@bp.route('/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '', type=str).strip()

    # Sevier page/per_page na URL, fazemos paginação.
    # Se NÃO vier page, devolvemos tudo.
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)

    query = Product.query

    # filtro de busca por nome ou tipo
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Product.name).like(like),
                func.lower(Product.type).like(like),
            )
        )

    # ----- MODO PAGINADO (usado na página pública) -----
    if page is not None and per_page is not None:
        pagination = query.order_by(Product.id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        products = pagination.items
        total = pagination.total
        pages = pagination.pages
        current_page = page

    # ----- MODO "TUDO" (usado hoje no admin) -----
    else:
        products = query.order_by(Product.id).all()
        total = len(products)
        pages = 1
        current_page = 1
        per_page = total if total > 0 else 1

    print(
        f"Rota /products | search='{search}' "
        f"| page={current_page} | per_page={per_page} | total={total}"
    )

    return jsonify({
        'message': 'Lista de produtos',
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'description': p.description,
                'type': p.type,
                'image_url': p.image_url,
                'video_url': p.video_url,
            }
            for p in products
        ],
        'page': current_page,
        'per_page': per_page,
        'total': total,
        'pages': pages,
    }), 200


@bp.route('/products/<int:product_id>', methods=['GET']) #RETORNA OS DETALHES DE UM PRODUTO ESPECÍFICO USANDO O ID
def get_product_by_id(product_id):
    # READ (detalhe) de um único produto pelo ID
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404

    # Retorna os dados do produto específico
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description,
        'type': product.type,
        'image_url': product.image_url,
        'video_url': product.video_url,
        #'stock': product.stock
    }), 200


@bp.route('/tips', methods=['GET']) #LISTA DAS DICAS CADASTRADAS NO SISTEMA.
def get_tips():
    # READ de todas as dicas disponíveis
    tips = Tip.query.all()
    print("Rota /tips chamada")
    return jsonify({
        'message': 'Lista de dicas',
        'tips': [{'id': t.id, 'title': t.title, 'content': t.content, 'category': t.category} 
                 for t in tips]
    })

@bp.route('/faqs', methods=['GET']) #LISTA DAS FAQS CADASTRADAS NO SISTEMA.
def get_faqs():
    # READ de todas as FAQs disponíveis
    faqs = FAQ.query.all()
    print("Rota /faqs chamada")
    return jsonify({
        'message': 'Lista de FAQs',
        'faqs': [
            {
                'id': f.id,
                'question': f.question,
                'answer': f.answer
            } 
            for f in faqs
        ]
    })

# ===================================
# LOGIN E USUÁRIOS
# ===================================

@bp.route('/users', methods=['POST']) #CRIA UM NOVO USUÁRIO NO SISTEMA.
def create_user():
    # CREATE de usuário comum (registro no sistema)
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    # Validação básica de campos obrigatórios
    if not username or not email or not password or not name:
        return jsonify({'error': 'username, email, password e name são obrigatórios'}), 400

    email_lower = email.lower()

    # Verifica se já existe usuário com mesmo username ou e-mail
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email_lower)
    ).first()
    
    if existing_user:
        if existing_user.username == username:
            return jsonify({'error': 'Nome de usuário já existe'}), 400
        else:
            return jsonify({'error': 'E-mail já cadastrado'}), 400

    # Gera hash da senha antes de salvar
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Cria o objeto User e salva no banco
    new_user = User(
        username=username, 
        email=email_lower,
        password_hash=password_hash, 
        name=name
    )
    db.session.add(new_user)
    db.session.commit()

    # Retorna dados básicos do usuário criado
    return jsonify({
        'message': 'Usuário cadastrado com sucesso',
        'user': {'id': new_user.id, 'username': new_user.username, 'name': new_user.name}
    })


@bp.route('/login', methods=['POST'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response, 200
        
    data = request.json
    login_identifier = data.get('username') 
    password = data.get('password')

    if not login_identifier or not password:
        return jsonify({'error': 'Identificador (username ou email) e senha são obrigatórios'}), 400

    login_identifier_lower = login_identifier.lower()

    user = User.query.filter(
        (User.username.ilike(login_identifier_lower)) | 
        (User.email == login_identifier_lower)
    ).first()

    # 🔒 SE NÃO EXISTIR OU ESTIVER INATIVO
    if not user:
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if not user.is_active:
        return jsonify({
            'error': 'Você foi inativado por condutas inadequadas, entre em contato com o suporte.'
        }), 403

    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'message': 'Login bem-sucedido',
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'is_admin': user.is_admin
            }
        })

    return jsonify({'error': 'Credenciais inválidas'}), 401


# ===================================
# ADMIN: PRODUTOS 
# ===================================

@bp.route('/admin/products', methods=['POST', 'OPTIONS']) #ADMIN PODE CRIAR UM PRODUTO.
@jwt_required(optional=True)
def create_product():
    # CREATE de produto (apenas admin). Também trata preflight CORS.
    if request.method == 'OPTIONS': # O navegador testa a rota antes de enviar dados
        # 🔓 Resposta ao preflight CORS
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200

    # 🔒 Verifica admin
    admin_check = admin_required()
    if admin_check:
        return admin_check

    # Dados do novo produto vindos do frontend
    data = request.get_json()
    new_product = Product(
        name=data.get("name"),
        price=float(data.get("price", 0)),
        #stock=int(data.get("stock", 0)),
        type=data.get("type"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        video_url=data.get("video_url")
    )
    db.session.add(new_product)
    db.session.commit()

    # Retorna produto criado
    response = jsonify({
        "message": "Produto criado com sucesso!",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price,
            "description": new_product.description,
            "type": new_product.type,
            "image_url": new_product.image_url,
            "video_url": new_product.video_url,

        }
    })
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 201

@bp.route('/admin/products/<int:product_id>', methods=['PUT', 'OPTIONS']) #ADMIN PODE EDITAR UM PRODUTO.
@jwt_required(optional=True)
def update_product(product_id):
    # UPDATE de produto (apenas admin)
    if request.method == 'OPTIONS':
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200

    # 🔒 Verifica admin
    admin_check = admin_required()
    if admin_check:
        return admin_check

    data = request.get_json()
    product = Product.query.get(product_id)

    # Verifica se o produto existe
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    # Atualiza apenas os campos enviados no corpo da requisição
    if "name" in data: product.name = data["name"]
    if "price" in data: product.price = float(data["price"])
    if "description" in data: product.description = data["description"]
    if "type" in data: product.type = data["type"]
    if "image_url" in data: product.image_url = data["image_url"]
    if "video_url" in data: product.video_url = data["video_url"]
    

    db.session.commit()

    # Retorna produto atualizado
    response = jsonify({
        "message": "Produto atualizado com sucesso!",
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "type": product.type,
            "image_url": product.image_url,
            "video_url": product.video_url,
            #"stock": product.stock
        }
    })
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200

@bp.route('/admin/products/<int:product_id>', methods=['DELETE', 'OPTIONS']) #Admin pode deletar um produto específico.
@jwt_required()
def delete_product(product_id):
    # --- CORS PREFlight ---
    if request.method == 'OPTIONS':
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200

    # --- Verifica se é admin ---
    admin_check = admin_required()
    if admin_check:
        return admin_check

    # --- Busca o produto ---
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    try:
        # --- APAGA DEPENDÊNCIAS ANTES (REVIEW, FAVORITOS, ETC.) ---
        Review.query.filter_by(product_id=product_id).delete()
        Favorite.query.filter_by(product_id=product_id).delete()
        # Se tiver mais tabelas:

        # --- APAGA O PRODUTO ---
        db.session.delete(product)
        db.session.commit()

        # --- Resposta de sucesso ---
        response = jsonify({"message": "Produto excluído com sucesso!"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    except Exception as e:
        db.session.rollback()
        print(f"[ERRO] Falha ao deletar produto {product_id}: {e}")
        return jsonify({"error": "Erro interno ao excluir produto"}), 500

# ===================================
# OUTRAS ROTAS ADMIN
# ===================================

@bp.route('/admin/tips', methods=['POST']) # Admin cria uma nova dica
@jwt_required()
def create_tip():
    # CREATE de dica (apenas admin)
    admin_check = admin_required()
    if admin_check:
        return admin_check

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')

    # Validação básica de campos obrigatórios
    if not title or not content:
        return jsonify({'error': 'title e content são obrigatórios'}), 400

    # Cria e salva nova dica
    new_tip = Tip(title=title, content=content, category=category)
    db.session.add(new_tip)
    db.session.commit()

    return jsonify({'message': 'Dica criada com sucesso', 'tip': {'id': new_tip.id, 'title': new_tip.title}})


@bp.route('/admin/faqs', methods=['POST']) # Admin cria uma nova FAQ
@jwt_required()
def create_faq():
    # CREATE de FAQ (apenas admin)
    admin_check = admin_required()
    if admin_check:
        return admin_check

    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    # Validação básica
    if not question or not answer:
        return jsonify({'error': 'question e answer são obrigatórios'}), 400

    # Cria e salva nova FAQ
    new_faq = FAQ(question=question, answer=answer)
    db.session.add(new_faq)
    db.session.commit()

    return jsonify({'message': 'FAQ criado com sucesso', 'faq': {'id': new_faq.id, 'question': new_faq.question}})

@bp.route('/admin/faqs/<int:faq_id>', methods=['DELETE', 'OPTIONS']) # Admin exclui uma FAQ específica
@jwt_required()
def delete_faq(faq_id):
    # DELETE de FAQ por ID (apenas admin). Também trata preflight CORS.
    if request.method == 'OPTIONS':
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200

    admin_check = admin_required()
    if admin_check:
        return admin_check

    # Busca FAQ pelo ID
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"error": "FAQ não encontrado"}), 404

    # Remove FAQ do banco
    db.session.delete(faq)
    db.session.commit()

    response = jsonify({"message": "FAQ deletado com sucesso"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200

@bp.route('/admin/users', methods=['GET'])  # Admin visualiza todos os usuários cadastrados (COM BUSCA)
def get_all_users():
    try:
        # pega ?search= da URL
        search = request.args.get('search', '', type=str).strip()

        query = User.query

        if search:
            like = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(User.name).like(like),
                    func.lower(User.username).like(like),
                    func.lower(User.email).like(like),
                )
            )

        users = query.all()

        users_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "name": user.name,
                "is_active": user.is_active,   #  AQUI
            }
            for user in users
        ]

        print(f"Rota /admin/users | search='{search}' | resultados={len(users_data)}")

        return jsonify({"users": users_data}), 200

    except Exception as e:
        print("Erro ao buscar usuários:", e)
        return jsonify({"error": "Erro ao buscar usuários"}), 500


@bp.route('/admin/users', methods=['POST', 'OPTIONS']) # Admin cria um novo usuário administrador
@jwt_required()
def create_admin_user():
    # CREATE de um novo usuário administrador
    if request.method == 'OPTIONS':
        return cors_response(), 200

    # Garante que apenas admin pode criar outro admin
    admin_check = admin_required()
    if admin_check:
        return admin_check

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    # Validação básica dos campos
    if not username or not email or not password or not name:
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

    if len(password) < 6:
        return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400

    email_lower = email.lower()
    # Verifica se username ou email já existem
    if User.query.filter((User.username == username) | (User.email == email_lower)).first():
         return jsonify({'error': 'Nome de usuário ou e-mail já estão em uso'}), 400

    try:
        # Gera hash da senha
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        # Cria usuário com flag is_admin = True
        new_admin = User(
            name=name,
            username=username,
            email=email_lower,
            password_hash=password_hash,
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()

        return jsonify({
            'message': 'Administrador criado com sucesso!',
            'user': {'id': new_admin.id, 'username': new_admin.username, 'is_admin': True}
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar admin: {e}")
        return jsonify({'error': 'Erro interno ao criar administrador'}), 500

@bp.route("/admin/stats", methods=["GET"]) # Admin visualiza estatísticas gerais do sistema (produtos, usuários, etc.)
@jwt_required()
def get_admin_stats():
    """Retorna estatísticas gerais para o dashboard (produtos, usuários, dicas, etc)"""
    # Somente admin pode acessar as estatísticas gerais
    admin_check = admin_required()
    if admin_check:
        return admin_check

    try:
        # Faz contagem de várias entidades para o dashboard
        total_products = Product.query.count()
        total_users = User.query.count()
        total_tips = Tip.query.count()
        total_reviews = Review.query.count()
        total_favorites = Favorite.query.count()

        return jsonify({
            "total_products": total_products,
            "total_users": total_users,
            "total_tips": total_tips,
            "total_reviews": total_reviews,
            "total_favorites": total_favorites
        }), 200
    except Exception as e:
        print("Erro ao buscar estatísticas:", e)
        return jsonify({"error": "Erro ao buscar estatísticas"}), 500


@bp.route("/admin/user-growth", methods=["GET"]) # Admin visualiza o crescimento de usuários por mês
@jwt_required()
def get_user_growth():
    """Retorna crescimento de usuários por mês para o gráfico"""
    # Somente admin pode visualizar o gráfico de crescimento de usuários
    admin_check = admin_required()
    if admin_check:
        return admin_check

    try:
        from sqlalchemy import extract, func

        # Agrupa usuários por ano e mês de criação
        growth_data = (
            db.session.query(
                extract("year", User.created_at).label("year"),
                extract("month", User.created_at).label("month"),
                func.count(User.id).label("total")
            )
            .group_by("year", "month")
            .order_by("year", "month")
            .all()
        )

        # Formata para o frontend (dashboard)
        formatted_data = [
            {"year": int(year), "month": int(month), "total": total}
            for year, month, total in growth_data
        ]

        return jsonify({"growth": formatted_data}), 200
    except Exception as e:
        print("Erro ao buscar crescimento de usuários:", e)
        return jsonify({"error": "Erro ao buscar crescimento de usuários"}), 500
    
@bp.route("/admin/product-ratings", methods=["GET"]) # Admin visualiza distribuição de notas dos produtos
@jwt_required()
def get_product_ratings():
    """Retorna a contagem de produtos por nota (1-5)"""
    # Somente admin pode ver a distribuição de notas (para o gráfico)
    admin_check = admin_required()
    if admin_check:
        return admin_check
    try:
        # Subquery que calcula média de nota por produto (arredondada)
        avg_ratings_subquery = db.session.query(
            Review.product_id,
            func.round(func.avg(Review.rating)).label('avg_rating')
        ).filter(Review.rating != None).group_by(Review.product_id).subquery()

        # Conta quantos produtos têm cada nota média
        ratings_distribution = db.session.query(
            avg_ratings_subquery.c.avg_rating.label('rating'),
            func.count(avg_ratings_subquery.c.product_id).label('count')
        ).group_by(avg_ratings_subquery.c.avg_rating).order_by(avg_ratings_subquery.c.avg_rating).all()
        formatted_data = [
            {"rating": int(r.rating), "count": r.count}
            for r in ratings_distribution if r.rating is not None
        ]
        # Garante que sempre haja faixas de 1 a 5, mesmo com 0
        final_data_map = {r['rating']: r['count'] for r in formatted_data}
        final_data = [
            {"rating": i, "count": final_data_map.get(i, 0)}
            for i in range(1, 6)
        ]
        return jsonify({"ratings": final_data}), 200

    except Exception as e:
        print("Erro ao buscar notas de produtos:", e)
        return jsonify({"error": "Erro ao buscar notas de produtos"}), 500
    
@bp.route('/admin/users/<int:user_id>', methods=['DELETE', 'OPTIONS']) # Admin exclui outro usuário específico
@jwt_required()
def delete_user_by_admin(user_id):
    """
    Permite que um administrador exclua a conta de outro usuário.
    """
    # DELETE de usuário por um admin (não permite apagar a si mesmo por aqui)
    if request.method == 'OPTIONS':
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200

    admin_check = admin_required()
    if admin_check:
        return admin_check

    admin_user_id = get_jwt_identity()

    # Admin não pode deletar a própria conta por esta rota
    if str(admin_user_id) == str(user_id):
        return jsonify({"error": "Administradores não podem excluir a própria conta por esta rota."}), 403

    # Busca o usuário a ser deletado
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({"error": "Usuário não encontrado"}), 404

    try:
        # Remove relações de favoritos e reviews antes de apagar o usuário
        Favorite.query.filter_by(user_id=user_id).delete()
        Review.query.filter_by(user_id=user_id).delete()

        db.session.delete(user_to_delete)
        db.session.commit()
        
        return jsonify({"message": "Usuário excluído com sucesso."}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir usuário (Admin): {e}")
        return jsonify({"error": "Erro interno ao excluir usuário."}), 500

# ===================================
# FAVORITOS
# ===================================

def cors_response(msg="CORS preflight ok"):
    # Função auxiliar para responder a requisições de preflight CORS
    response = jsonify({"msg": msg})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
    return response

@bp.route("/favorites", methods=["GET"])  # GET: lista favoritos do usuário logado
@jwt_required()
def get_favorites():
    # Pega o ID do usuário logado (via JWT)
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Usuário não autenticado"}), 401

    try:
        # Busca todos os favoritos do usuário
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        products = []

        for fav in favorites:
            product = Product.query.get(fav.product_id)
            if product:
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "description": product.description,
                    "image_url": product.image_url,
                    "video_url": product.video_url,
                    "type": product.type,
                    # "stock": product.stock
                })

        response = jsonify({
            "message": "Favoritos do usuário",
            "favorites": products
        })
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    except Exception as e:
        print("Erro em GET /favorites:", e)
        return jsonify({"error": "Erro ao processar favoritos"}), 500


@bp.route("/favorites", methods=["POST", "OPTIONS"])  # POST: adiciona favorito / OPTIONS: preflight CORS
@jwt_required()
def add_favorite():
    # OPTIONS → teste CORS antes do POST
    if request.method == "OPTIONS":
        response = jsonify({"msg": "CORS preflight ok"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response, 200

    # POST → adicionar novo favorito
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Usuário não autenticado"}), 401

    try:
        data = request.get_json()
        product_id = data.get("product_id")
        if not product_id:
            return jsonify({"error": "product_id é obrigatório"}), 400

        # Não duplica favoritos
        existing_fav = Favorite.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()
        if existing_fav:
            return jsonify({"message": "Produto já favoritado"}), 200

        # Cria favorito
        new_fav = Favorite(
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.now()
        )
        db.session.add(new_fav)
        db.session.commit()

        response = jsonify({"message": "Produto adicionado aos favoritos"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 201

    except Exception as e:
        print("Erro em POST /favorites:", e)
        return jsonify({"error": "Erro ao processar favoritos"}), 500

@bp.route("/favorites/<int:product_id>", methods=["DELETE", "OPTIONS"]) # Remove um produto dos favoritos (Estando LOGADO)
@jwt_required()  # usuário deve estar logado
def remove_favorite(product_id):
    # DELETE: remove um produto dos favoritos do usuário logado
    if request.method == "OPTIONS":
        return cors_response(), 200

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Usuário não autenticado"}), 401

    try:
        # Procura o favorito correspondente
        fav = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
        if not fav:
            return jsonify({"error": "Favorito não encontrado"}), 404

        # Deleta favorito
        db.session.delete(fav)
        db.session.commit()

        response = jsonify({"message": "Produto removido dos favoritos"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    except Exception as e:
        print("Erro em /favorites/<id>:", e)
        return jsonify({"error": "Erro ao remover favorito"}), 500

# ===================================
# COMENTÁRIOS
# ===================================

@bp.route('/products/<int:product_id>/reviews', methods=['GET']) # Lista todos os comentários de um produto
def get_reviews(product_id):
    # READ: lista comentários (reviews) de um determinado produto
    reviews = Review.query.filter_by(product_id=product_id).join(User).add_columns(
        Review.id,
        Review.user_id,
        User.name,
        Review.comment,
        Review.created_at).order_by(Review.created_at.desc()).all()
    review_list = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "user_name": r.name,
            "comment": r.comment,
            "created_at": r.created_at.strftime('%d/%m/%Y %H:%M')
        }
        for r in reviews
    ]
    return jsonify(review_list), 200

# No topo do routes.py
try:
    from app.utils.banned_words import contains_banned_word, censor_text
except Exception:
    def contains_banned_word(text: str) -> bool:
        return False

    def censor_text(text: str) -> str:
        return text

@bp.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(product_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    comment = data.get('comment', '').strip()

    if not comment:
        return jsonify({'error': 'Comentário é obrigatório'}), 400

    # BLOQUEIA PALAVRAS PROIBIDAS
    if contains_banned_word(comment):
        return jsonify({
            'error': 'Comentário contém palavras não permitidas. Por favor, revise seu texto.'
        }), 400

    # OPCIONAL: CENSURAR E SALVAR
    # clean_comment = censor_text(comment)
    # new_review = Review(..., comment=clean_comment)

    new_review = Review(
        product_id=product_id,
        user_id=current_user_id,
        comment=comment,
        created_at=datetime.utcnow()
    )
    db.session.add(new_review)
    db.session.commit()

    return jsonify({'message': 'Comentário adicionado com sucesso'}), 201

@bp.route('/products/<int:product_id>/reviews/<int:review_id>', methods=['DELETE']) # Usuário (ou admin) exclui um comentário específico
@jwt_required()
def delete_review(product_id, review_id):
    # DELETE: remove um comentário específico, desde que seja do próprio usuário ou admin
    user_id = int(get_jwt_identity())
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 401

    # Busca o review pelo produto e ID
    review = Review.query.filter_by(id=review_id, product_id=product_id).first()
    if not review:
        return jsonify({"error": "Comentário não encontrado"}), 404

    # Só o autor do comentário ou admin podem apagar
    if review.user_id != user.id and not user.is_admin:
        return jsonify({"error": "Não autorizado a deletar este comentário"}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Comentário deletado com sucesso"}), 200

# ===================================
# NOTAS
# ===================================

@bp.route('/products/<int:product_id>/rating', methods=['POST']) # Usuário dá uma nota entre 1 e 5 para o produto
@jwt_required()
def rate_product(product_id):
    # CREATE/UPDATE de nota (rating) para um produto
    user_id = int(get_jwt_identity())
    data = request.get_json()
    rating = data.get('rating')

    # Valida faixa de nota entre 1 e 5
    if rating is None or not (1 <= rating <= 5):
        return jsonify({'error': 'A nota deve ser entre 1 e 5'}), 400

    # Se usuário já avaliou, só atualiza; senão, cria novo registro
    review = Review.query.filter_by(product_id=product_id, user_id=user_id).first()

    if review:
        review.rating = rating
        review.created_at = datetime.utcnow()
    else:
        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            created_at=datetime.utcnow()
        )
        db.session.add(review)

    db.session.commit()
    return jsonify({'message': 'Nota registrada com sucesso'}), 200

@bp.route('/products/<int:product_id>/rating', methods=['GET']) # Retorna a média de notas do produto
def get_product_rating(product_id):
    # READ: retorna média e quantidade de avaliações de um produto
    ratings = Review.query.filter_by(product_id=product_id).with_entities(Review.rating).all()
    if not ratings:
        return jsonify({'average': None, 'count': 0}), 200

    values = [r.rating for r in ratings if r.rating is not None]
    if not values:
        return jsonify({'average': None, 'count': 0}), 200

    # Calcula média com uma casa decimal
    avg = round(sum(values) / len(values), 1)
    return jsonify({'average': avg, 'count': len(values)}), 200

# ===================================
# MINHA CONTA
# ===================================

@bp.route("/user/me", methods=["GET"]) # Retorna dados do usuário logado
@jwt_required()
def get_current_user():
    # READ: dados do usuário logado (perfil)
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Retorna informações básicas do usuário
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    })

@bp.route("/user/update", methods=["PUT"]) # Usuário atualiza seus próprios dados
@jwt_required()
def update_user():
    # UPDATE do perfil do usuário logado
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json()

    # Atualiza apenas os campos enviados
    user.name = data.get("name", user.name)
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)

    db.session.commit()
    return jsonify({"message": "Usuário atualizado com sucesso!"})

@bp.route("/user/change-password", methods=["POST"]) # Usuário troca sua própria senha
@jwt_required()
def change_password():
    """
    Permite que o usuário logado altere sua própria senha.
    Exige a senha atual.
    """
    # UPDATE de senha para o usuário logado
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Verifica se ambos os campos foram enviados
    if not current_password or not new_password:
        return jsonify({"error": "Senha atual e nova senha são obrigatórias"}), 400

    # Confere se a senha atual está correta
    if not bcrypt.check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Senha atual incorreta"}), 401

    # Valida tamanho mínimo da nova senha
    if len(new_password) < 6:
        return jsonify({"error": "A nova senha deve ter pelo menos 6 caracteres"}), 400

    # Atualiza hash de senha no banco
    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Senha alterada com sucesso!"}), 200


@bp.route("/user/delete-account", methods=["DELETE"]) # Usuário exclui sua própria conta
@jwt_required()
def delete_account():
    """
    Permite que o usuário logado exclua sua própria conta.
    Admins não podem ser excluídos por esta rota.
    """
    # DELETE da própria conta do usuário (exceto admins)
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    if user.is_admin:
        return jsonify({"error": "Contas de administrador não podem ser excluídas por esta rota."}), 403

    try:
        # Limpa relacionamentos (favoritos e reviews) antes de remover o usuário
        Favorite.query.filter_by(user_id=user.id).delete()
        Review.query.filter_by(user_id=user.id).delete()

        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Conta excluída com sucesso."}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir conta: {e}")
        return jsonify({"error": "Erro ao excluir conta. Verifique as dependências do banco de dados."}), 500

# ===================================
# IA - CHAT BOT
# ===================================
try:
    # Lê a chave de API do Gemini a partir da variável de ambiente
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi encontrada.")

    # Configura cliente do Google Generative AI
    genai.configure(api_key=api_key)

    # Prompt de sistema definindo personalidade e regras do bot "Pi"
    SYSTEM_PROMPT = """
    Você é 'Pi', um assistente virtual especializado da 'PiFloor Pisos'.
    Sua personalidade é prestativa, amigável e focada no cliente.
    SUA TAREFA PRINCIPAL: Ajudar clientes com dúvidas sobre pisos, decoração e os produtos da PiFloor.

    REGRAS ESTRITAS:
    1.  NÃO responda, sob nenhuma hipótese, perguntas sobre tópicos não relacionados a pisos, construção, decoração ou à empresa PiFloor (ex: futebol, política, drogas, notícias, etc.).
    2.  Se perguntado sobre tópicos proibidos, recuse educadamente. Ex: "Desculpe, eu só consigo ajudar com perguntas sobre pisos e nossos produtos."
    3.  Use o "Contexto do Banco de Dados" fornecido para responder perguntas sobre o catálogo da PiFloor.
    4.  Se a pergunta do usuário for vaga (ex: "e aí?"), apresente-se e pergunte como pode ajudar com pisos.
    5.  MANTENHA AS RESPOSTAS BREVES E DIRETAS. Tente responder em 2-3 frases, a menos que o usuário peça especificamente por mais detalhes.
    """

    # Configurações de geração de texto (criatividade, tamanho, etc.)
    generation_config = {
      "temperature": 0.7,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }

    # Nome do modelo do Gemini a ser usado
    MODEL_NAME = "models/gemini-2.5-flash" 
    
    # Cria o modelo e inicia uma sessão de chat
    model = genai.GenerativeModel(
        model_name=MODEL_NAME, 
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT
    )
    
    chat_session = model.start_chat(history=[])
    print(f"✅ Sessão de Chatbot Gemini ({MODEL_NAME}) inicializada com sucesso.")

except Exception as e:
    # Caso algo dê errado na inicialização, o chatbot fica desativado
    print(f"❌ ERRO CRÍTICO AO INICIALIZAR O CLIENTE GEMINI: {e}")
    chat_session = None

def _get_cheapest_product():
    """Busca o produto mais barato no banco de dados."""
    # Função auxiliar para buscar o piso com menor preço
    try:
        min_price = db.session.query(func.min(Product.price)).scalar()
        if not min_price:
            return None
        
        product = Product.query.filter_by(price=min_price).first()
        if product:
            return f"O produto mais barato é '{product.name}' por R${product.price:.2f}/m²."
    except Exception as e:
        print(f"Erro ao buscar produto mais barato: {e}")
    return None

def _get_product_by_type(tipo):
    """Busca produtos por tipo (ex: 'laminado')"""
    # Função auxiliar para listar alguns produtos de um tipo específico
    try:
        products = Product.query.filter(Product.type.ilike(f"%{tipo}%")).limit(3).all()
        if products:
            names = ", ".join([p.name for p in products])
            return f"Alguns de nossos pisos do tipo {tipo} são: {names}."
    except Exception as e:
        print(f"Erro ao buscar por tipo: {e}")
    return None

@bp.route("/chat", methods=["POST"]) # Envia a mensagem do usuário para o chatbot e retorna a resposta da IA
@jwt_required(optional=True)
def handle_chat():
    # Endpoint principal do chatbot: recebe mensagem do usuário e responde usando o Gemini
    if not chat_session:
        print("Erro: Sessão de chat do Gemini não inicializada.")
        return jsonify({"error": "Desculpe, o serviço de IA não está configurado."}), 500

    try:
        data = request.get_json()
        user_message = data.get("message")

        # Garante que veio alguma mensagem
        if not user_message:
            return jsonify({"error": "Mensagem não fornecida."}), 400

        context_from_db = ""
        user_message_lower = user_message.lower()

        # Regras simples para enriquecer o contexto usando o banco de dados
        if "mais barato" in user_message_lower or "menor preço" in user_message_lower:
            context_from_db = _get_cheapest_product()
        elif "piso laminado" in user_message_lower:
            context_from_db = _get_product_by_type('laminado')
        elif "piso vinílico" in user_message_lower:
            context_from_db = _get_product_by_type('vinilico')

        # Monta o prompt final unindo contexto + pergunta do usuário
        final_prompt = f"""
        Contexto do Banco de Dados:
        '{context_from_db if context_from_db else "Nenhum contexto específico do banco de dados."}'
        
        Pergunta do Usuário:
        '{user_message}'
        """
        
        # Envia para o modelo do Gemini e recebe resposta
        response = chat_session.send_message(final_prompt)

        return jsonify({"reply": response.text}), 200

    except Exception as e:
        print(f"Erro na API do Gemini (endpoint /chat): {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/tips/<int:tip_id>', methods=['PUT']) # Admin (ID 7) edita uma dica específica
@jwt_required()
def update_tip(tip_id):
    # UPDATE de dica pelo admin ID 7 (apenas campos enviados no JSON)
    check = admin_7_required()
    if check:
        return check

    data = request.get_json() or {}  # evita erro se vier vazio
    tip = Tip.query.get_or_404(tip_id)

    # Atualiza APENAS o que veio no JSON (não precisa mandar tudo)
    if 'title' in data:
        tip.title = data['title']
    if 'content' in data:
        tip.content = data['content']
    if 'category' in data:
        tip.category = data['category']

    db.session.commit()
    return jsonify({"msg": "Dica atualizada com sucesso!"}), 200

@bp.route('/admin/tips/<int:tip_id>', methods=['DELETE']) # Admin (ID 7) exclui uma dica específica
@jwt_required()
def delete_tip(tip_id):
    # DELETE de dica, restrito ao admin ID 7
    # Só o admin ID 7 pode excluir
    check = admin_7_required()
    if check:
        return check

    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    return jsonify({"msg": "Dica excluída com sucesso!"}), 200

@bp.route('/admin/faqs/<int:faq_id>', methods=['PUT']) # Admin (ID 7) edita uma FAQ específica
@jwt_required()
def update_faq(faq_id):
    # UPDATE de FAQ, também restrito ao admin ID 7
    check = admin_7_required()
    if check:
        return check

    data = request.get_json() or {}
    faq = FAQ.query.get_or_404(faq_id)

    # Atualiza apenas os campos enviados
    if 'question' in data:
        faq.question = data['question']
    if 'answer' in data:
        faq.answer = data['answer']

    db.session.commit()
    return jsonify({"msg": "FAQ atualizada com sucesso!"}), 200


@bp.route('/admin/users/<int:user_id>/status', methods=['PUT']) #Atualiza o status de atividade de um usuário (ativa/inativa conta)
@jwt_required()
def update_user_status(user_id):
    """
    Admin ativa ou inativa um usuário (is_active = True/False)
    """
    #Verifica se o usuário logado é admin
    admin_check = admin_required()
    if admin_check:
        #Se não for admin, retorna o erro apropriado
        return admin_check

    #Obtém o ID do usuário logado a partir do token JWT
    admin_user_id = get_jwt_identity()

    # impedir que o admin mude o próprio status
    if str(admin_user_id) == str(user_id):
        return jsonify({"error": "Você não pode alterar o próprio status."}), 403

    data = request.get_json() or {}
    if "is_active" not in data:
        return jsonify({"error": "Campo 'is_active' é obrigatório (true/false)."}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        user.is_active = bool(data["is_active"])
        db.session.commit()

        status_txt = "ativado" if user.is_active else "inativado"
        return jsonify({
            "message": f"Usuário {status_txt} com sucesso.",
            "user": {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "is_active": user.is_active
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Erro ao atualizar status do usuário:", e)
        return jsonify({"error": "Erro ao atualizar status do usuário"}), 500
