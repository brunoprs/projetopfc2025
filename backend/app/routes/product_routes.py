"""
Rotas de produtos (públicas e administrativas).

Este módulo contém endpoints relacionados a produtos.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_cors import CORS
from ..services import ProductService
from ..decorators import admin_required
from ..constants import (
    ALLOWED_ORIGINS,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_NOT_FOUND
)

product_bp = Blueprint("products", __name__)
CORS(product_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


@product_bp.route('/products', methods=['GET'])
def get_products():
    """
    Retorna lista de produtos com suporte a busca e paginação.
    
    Query Parameters:
        search (str): Termo de busca (nome ou tipo)
        page (int): Número da página (opcional)
        per_page (int): Itens por página (opcional)
    
    Returns:
        200: Lista de produtos com metadados de paginação
    """
    search = request.args.get('search', '', type=str).strip()
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)
    
    result = ProductService.get_products_paginated(search, page, per_page)
    
    return jsonify({
        'message': 'Lista de produtos',
        **result
    }), HTTP_OK


@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """
    Retorna detalhes de um produto específico.
    
    Path Parameters:
        product_id (int): ID do produto
    
    Returns:
        200: Dados do produto
        404: Produto não encontrado
    """
    product = ProductService.get_product_by_id(product_id)
    
    if not product:
        return jsonify({'error': ERROR_MESSAGES['PRODUCT_NOT_FOUND']}), HTTP_NOT_FOUND
    
    return jsonify(product.to_dict()), HTTP_OK


@product_bp.route('/admin/products', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
@admin_required
def create_product():
    """
    Cria um novo produto (apenas admin).
    
    Request Body:
        name (str): Nome do produto
        price (float): Preço
        type (str): Tipo do produto
        description (str): Descrição (opcional)
        image_url (str): URL da imagem (opcional)
        video_url (str): URL do vídeo (opcional)
    
    Returns:
        201: Produto criado com sucesso
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK
    
    data = request.get_json()
    
    product = ProductService.create_product(
        name=data.get("name"),
        price=data.get("price", 0),
        type=data.get("type"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        video_url=data.get("video_url")
    )
    
    return jsonify({
        "message": SUCCESS_MESSAGES['PRODUCT_CREATED'],
        "product": product.to_dict()
    }), HTTP_CREATED


@product_bp.route('/admin/products/<int:product_id>', methods=['PUT', 'OPTIONS'])
@jwt_required(optional=True)
@admin_required
def update_product(product_id):
    """
    Atualiza um produto existente (apenas admin).
    
    Path Parameters:
        product_id (int): ID do produto
    
    Request Body:
        Campos a serem atualizados (name, price, type, description, image_url, video_url)
    
    Returns:
        200: Produto atualizado com sucesso
        404: Produto não encontrado
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK
    
    data = request.get_json()
    
    product = ProductService.update_product(product_id, **data)
    
    if not product:
        return jsonify({'error': ERROR_MESSAGES['PRODUCT_NOT_FOUND']}), HTTP_NOT_FOUND
    
    return jsonify({
        "message": SUCCESS_MESSAGES['PRODUCT_UPDATED'],
        "product": product.to_dict()
    }), HTTP_OK


@product_bp.route('/admin/products/<int:product_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required(optional=True)
@admin_required
def delete_product(product_id):
    """
    Exclui um produto (apenas admin).
    
    Path Parameters:
        product_id (int): ID do produto
    
    Returns:
        200: Produto excluído com sucesso
        404: Produto não encontrado
    """
    if request.method == 'OPTIONS':
        return jsonify({"msg": "CORS preflight ok"}), HTTP_OK
    
    success = ProductService.delete_product(product_id)
    
    if not success:
        return jsonify({'error': ERROR_MESSAGES['PRODUCT_NOT_FOUND']}), HTTP_NOT_FOUND
    
    return jsonify({"message": SUCCESS_MESSAGES['PRODUCT_DELETED']}), HTTP_OK
