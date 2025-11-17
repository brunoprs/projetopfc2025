"""
Rotas públicas (dicas, FAQs, redes sociais).

Este módulo contém endpoints públicos que não requerem autenticação.
"""
import logging
from flask import Blueprint, jsonify
from flask_cors import CORS
from ..models import Tip, FAQ, SocialMedia
from ..constants import ALLOWED_ORIGINS, HTTP_OK

logger = logging.getLogger(__name__)

public_bp = Blueprint("public", __name__)
CORS(public_bp, supports_credentials=True, origins=ALLOWED_ORIGINS)


# ===================================
# DICAS (TIPS)
# ===================================

@public_bp.route('/tips', methods=['GET'])
def get_tips():
    """
    Lista todas as dicas disponíveis.
    
    Returns:
        200: Lista de dicas
    """
    tips = Tip.query.all()
    
    logger.info(f"Rota /tips chamada - {len(tips)} dicas retornadas")
    
    return jsonify({
        'message': 'Lista de dicas',
        'tips': [tip.to_dict() for tip in tips]
    }), HTTP_OK


# ===================================
# FAQs
# ===================================

@public_bp.route('/faqs', methods=['GET'])
def get_faqs():
    """
    Lista todas as perguntas frequentes.
    
    Returns:
        200: Lista de FAQs
    """
    faqs = FAQ.query.all()
    
    logger.info(f"Rota /faqs chamada - {len(faqs)} FAQs retornadas")
    
    return jsonify({
        'message': 'Lista de FAQs',
        'faqs': [faq.to_dict() for faq in faqs]
    }), HTTP_OK


# ===================================
# REDES SOCIAIS
# ===================================

@public_bp.route('/social-media', methods=['GET'])
def get_social_media():
    """
    Lista todas as redes sociais da empresa.
    
    Returns:
        200: Lista de redes sociais
    """
    social_media = SocialMedia.query.all()
    
    logger.info(f"Rota /social-media chamada - {len(social_media)} redes retornadas")
    
    return jsonify({
        'message': 'Lista de redes sociais',
        'social_media': [sm.to_dict() for sm in social_media]
    }), HTTP_OK
