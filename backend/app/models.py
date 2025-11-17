"""
Modelos de dados da aplicação PiFloor.

Este módulo contém todas as classes de modelo ORM usando SQLAlchemy.
Cada modelo representa uma tabela no banco de dados e inclui métodos
de serialização para facilitar a conversão em JSON.
"""
from . import db
from datetime import datetime
from sqlalchemy import func


class Product(db.Model):
    """Modelo representando um produto de piso."""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    type = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    video_url = db.Column(db.String(200))
    
    # Relacionamentos
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Serializa o produto para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'type': self.type,
            'image_url': self.image_url,
            'video_url': self.video_url
        }
    
    def __repr__(self):
        """Representação string do produto para debug."""
        return f'<Product {self.id}: {self.name}>'


class User(db.Model):
    """Modelo representando um usuário do sistema."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    name = db.Column(db.String(120), nullable=False)
    
    # Relacionamentos
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email, password_hash, name, is_admin=False, is_active=True):
        """
        Inicializa um novo usuário.
        
        Args:
            username: Nome de usuário único
            email: Email único do usuário
            password_hash: Hash da senha (já criptografado)
            name: Nome completo do usuário
            is_admin: Se o usuário é administrador (padrão: False)
            is_active: Se a conta está ativa (padrão: True)
        """
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.is_admin = is_admin
        self.is_active = is_active

    def to_dict(self, include_sensitive=False):
        """
        Serializa o usuário para dicionário.
        
        Args:
            include_sensitive: Se deve incluir dados sensíveis como email (padrão: False)
        
        Returns:
            Dicionário com dados do usuário
        """
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
        
        if include_sensitive:
            data['email'] = self.email
            data['is_active'] = self.is_active
        
        return data
    
    @staticmethod
    def get_growth_by_month():
        """
        Retorna estatísticas de crescimento de usuários por mês.
        
        Returns:
            Lista de tuplas (ano, mês, total)
        """
        from sqlalchemy import extract
        return (
            db.session.query(
                extract("year", User.created_at).label("year"),
                extract("month", User.created_at).label("month"),
                func.count(User.id).label("total")
            )
            .group_by("year", "month")
            .order_by("year", "month")
            .all()
        )
    
    def __repr__(self):
        """Representação string do usuário para debug."""
        return f'<User {self.id}: {self.username}>'


class Review(db.Model):
    """Modelo representando uma avaliação de produto."""
    
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        """Serializa a avaliação para dicionário."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    @staticmethod
    def get_product_ratings_distribution():
        """
        Retorna a distribuição de avaliações por nota (1-5).
        
        Returns:
            Lista de dicionários com rating e count
        """
        avg_ratings_subquery = db.session.query(
            Review.product_id,
            func.round(func.avg(Review.rating)).label('avg_rating')
        ).filter(Review.rating != None).group_by(Review.product_id).subquery()

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
        return [
            {"rating": i, "count": final_data_map.get(i, 0)}
            for i in range(1, 6)
        ]
    
    def __repr__(self):
        """Representação string da avaliação para debug."""
        return f'<Review {self.id}: Product {self.product_id} - {self.rating}★>'


class Tip(db.Model):
    """Modelo representando uma dica sobre pisos."""
    
    __tablename__ = 'tips'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    def to_dict(self):
        """Serializa a dica para dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category
        }
    
    def __repr__(self):
        """Representação string da dica para debug."""
        return f'<Tip {self.id}: {self.title}>'


class FAQ(db.Model):
    """Modelo representando uma pergunta frequente."""
    
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.Text)
    
    def to_dict(self):
        """Serializa a FAQ para dicionário."""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer
        }
    
    def __repr__(self):
        """Representação string da FAQ para debug."""
        return f'<FAQ {self.id}: {self.question[:50]}...>'


class SocialMedia(db.Model):
    """Modelo representando um link de rede social."""
    
    __tablename__ = 'social_media'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200))
    
    def to_dict(self):
        """Serializa a rede social para dicionário."""
        return {
            'id': self.id,
            'platform': self.platform,
            'url': self.url
        }
    
    def __repr__(self):
        """Representação string da rede social para debug."""
        return f'<SocialMedia {self.id}: {self.platform}>'


class Favorite(db.Model):
    """Modelo representando um produto favorito de um usuário."""
    
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),)
    
    def to_dict(self):
        """Serializa o favorito para dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __repr__(self):
        """Representação string do favorito para debug."""
        return f'<Favorite {self.id}: User {self.user_id} - Product {self.product_id}>'
