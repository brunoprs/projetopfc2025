"""
Serviço de produtos.

Este módulo contém a lógica de negócio relacionada a produtos,
separando a lógica das rotas e facilitando testes e manutenção.
"""
import logging
from sqlalchemy import func, or_
from ..models import Product, db

logger = logging.getLogger(__name__)


class ProductService:
    """Serviço para gerenciar operações de produtos."""
    
    @staticmethod
    def get_products_paginated(search=None, page=None, per_page=None):
        """
        Retorna produtos com suporte a busca e paginação.
        
        Args:
            search: Termo de busca (nome ou tipo)
            page: Número da página (None para retornar todos)
            per_page: Itens por página (None para retornar todos)
        
        Returns:
            Dicionário com produtos e metadados de paginação
        """
        query = Product.query
        
        # Aplicar filtro de busca se fornecido
        if search:
            like_pattern = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Product.name).like(like_pattern),
                    func.lower(Product.type).like(like_pattern),
                )
            )
        
        # Modo paginado
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
        # Modo "todos os produtos"
        else:
            products = query.order_by(Product.id).all()
            total = len(products)
            pages = 1
            current_page = 1
            per_page = total if total > 0 else 1
        
        logger.info(
            f"ProductService.get_products_paginated | search='{search}' | "
            f"page={current_page} | per_page={per_page} | total={total}"
        )
        
        return {
            'products': [p.to_dict() for p in products],
            'page': current_page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
        }
    
    @staticmethod
    def get_product_by_id(product_id):
        """
        Retorna um produto específico pelo ID.
        
        Args:
            product_id: ID do produto
        
        Returns:
            Produto encontrado ou None
        """
        return Product.query.get(product_id)
    
    @staticmethod
    def create_product(name, price, type, description=None, image_url=None, video_url=None):
        """
        Cria um novo produto.
        
        Args:
            name: Nome do produto
            price: Preço do produto
            type: Tipo do produto
            description: Descrição (opcional)
            image_url: URL da imagem (opcional)
            video_url: URL do vídeo (opcional)
        
        Returns:
            Produto criado
        """
        new_product = Product(
            name=name,
            price=float(price),
            type=type,
            description=description,
            image_url=image_url,
            video_url=video_url
        )
        db.session.add(new_product)
        db.session.commit()
        
        logger.info(f"Produto criado: {new_product.id} - {new_product.name}")
        return new_product
    
    @staticmethod
    def update_product(product_id, **kwargs):
        """
        Atualiza um produto existente.
        
        Args:
            product_id: ID do produto
            **kwargs: Campos a serem atualizados
        
        Returns:
            Produto atualizado ou None se não encontrado
        """
        product = Product.query.get(product_id)
        if not product:
            return None
        
        # Atualiza apenas os campos fornecidos
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        db.session.commit()
        logger.info(f"Produto atualizado: {product.id} - {product.name}")
        return product
    
    @staticmethod
    def delete_product(product_id):
        """
        Exclui um produto.
        
        Args:
            product_id: ID do produto
        
        Returns:
            True se excluído, False se não encontrado
        """
        product = Product.query.get(product_id)
        if not product:
            return False
        
        db.session.delete(product)
        db.session.commit()
        logger.info(f"Produto excluído: {product_id}")
        return True
    
    @staticmethod
    def get_cheapest_product():
        """
        Retorna o produto mais barato.
        
        Returns:
            String descritiva do produto mais barato ou None
        """
        try:
            min_price = db.session.query(func.min(Product.price)).scalar()
            if not min_price:
                return None
            
            product = Product.query.filter_by(price=min_price).first()
            if product:
                return f"O produto mais barato é '{product.name}' por R${product.price:.2f}/m²."
        except Exception as e:
            logger.error(f"Erro ao buscar produto mais barato: {e}")
        return None
    
    @staticmethod
    def get_products_by_type(product_type, limit=3):
        """
        Retorna produtos de um tipo específico.
        
        Args:
            product_type: Tipo do produto
            limit: Número máximo de produtos a retornar
        
        Returns:
            String descritiva dos produtos ou None
        """
        try:
            products = Product.query.filter(
                Product.type.ilike(f"%{product_type}%")
            ).limit(limit).all()
            
            if products:
                names = ", ".join([p.name for p in products])
                return f"Alguns de nossos pisos do tipo {product_type} são: {names}."
        except Exception as e:
            logger.error(f"Erro ao buscar produtos por tipo: {e}")
        return None
