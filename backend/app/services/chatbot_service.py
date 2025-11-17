"""
Serviço de chatbot (Google Gemini é opcional).

Este módulo encapsula toda a lógica do chatbot. Se a biblioteca
google-generativeai não estiver instalada, o chatbot retornará
mensagens padrão baseadas em regras.
"""
import os
import logging
from ..constants import (
    CHATBOT_MODEL_NAME,
    CHATBOT_TEMPERATURE,
    CHATBOT_MAX_TOKENS,
    CHATBOT_SYSTEM_PROMPT
)
from .product_service import ProductService

logger = logging.getLogger(__name__)

# Tenta importar Gemini (opcional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Biblioteca google-generativeai não encontrada. Chatbot funcionará em modo básico.")


class ChatbotService:
    """Serviço para gerenciar o chatbot com IA (ou modo básico)."""
    
    def __init__(self):
        """Inicializa o serviço de chatbot."""
        self.chat_session = None
        self.use_gemini = False
        
        if GEMINI_AVAILABLE:
            self._initialize_gemini()
        else:
            logger.info("Chatbot iniciado em modo básico (sem IA)")
    
    def _initialize_gemini(self):
        """
        Configura e inicializa o cliente do Google Gemini (se disponível).
        
        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY não configurada. Usando chatbot em modo básico.")
                return False
            
            genai.configure(api_key=api_key)
            
            generation_config = {
                "temperature": CHATBOT_TEMPERATURE,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": CHATBOT_MAX_TOKENS,
            }
            
            model = genai.GenerativeModel(
                model_name=CHATBOT_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=CHATBOT_SYSTEM_PROMPT
            )
            
            self.chat_session = model.start_chat(history=[])
            self.use_gemini = True
            logger.info(f"Chatbot Gemini ({CHATBOT_MODEL_NAME}) inicializado com sucesso.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Gemini: {e}. Usando modo básico.")
            self.chat_session = None
            self.use_gemini = False
            return False
    
    def _get_context_from_database(self, user_message):
        """
        Enriquece o contexto com informações do banco de dados.
        
        Args:
            user_message: Mensagem do usuário
        
        Returns:
            String com contexto adicional ou None
        """
        user_message_lower = user_message.lower()
        
        # Detecta intenções e busca dados relevantes
        if "mais barato" in user_message_lower or "menor preço" in user_message_lower:
            return ProductService.get_cheapest_product()
        
        elif "piso laminado" in user_message_lower or "laminado" in user_message_lower:
            return ProductService.get_products_by_type('laminado')
        
        elif "piso vinílico" in user_message_lower or "vinílico" in user_message_lower or "vinilico" in user_message_lower:
            return ProductService.get_products_by_type('vinilico')
        
        return None
    
    def _basic_response(self, user_message):
        """
        Gera resposta básica sem IA (baseada em regras).
        
        Args:
            user_message: Mensagem do usuário
        
        Returns:
            Resposta padrão
        """
        user_message_lower = user_message.lower()
        
        # Respostas baseadas em palavras-chave
        if "mais barato" in user_message_lower or "menor preço" in user_message_lower:
            product_info = ProductService.get_cheapest_product()
            if product_info:
                return f"O produto mais barato disponível é: {product_info}"
            return "Desculpe, não encontrei informações sobre preços no momento."
        
        elif "laminado" in user_message_lower:
            products = ProductService.get_products_by_type('laminado')
            if products:
                return f"Temos pisos laminados disponíveis: {products}"
            return "Desculpe, não encontrei pisos laminados no momento."
        
        elif "vinilico" in user_message_lower or "vinílico" in user_message_lower:
            products = ProductService.get_products_by_type('vinilico')
            if products:
                return f"Temos pisos vinílicos disponíveis: {products}"
            return "Desculpe, não encontrei pisos vinílicos no momento."
        
        elif "ola" in user_message_lower or "olá" in user_message_lower or "oi" in user_message_lower:
            return "Olá! Como posso ajudá-lo com pisos hoje?"
        
        elif "obrigado" in user_message_lower or "obrigada" in user_message_lower:
            return "De nada! Estou aqui para ajudar."
        
        else:
            return "Desculpe, não entendi sua pergunta. Posso ajudá-lo com informações sobre nossos pisos laminados e vinílicos!"
    
    def send_message(self, user_message):
        """
        Processa uma mensagem do usuário e retorna a resposta.
        
        Args:
            user_message: Mensagem enviada pelo usuário
        
        Returns:
            Tupla (reply, error_message)
            reply será None se houver erro
        """
        if not user_message:
            return None, "Mensagem não fornecida."
        
        # Modo IA (Gemini)
        if self.use_gemini and self.chat_session:
            try:
                context_from_db = self._get_context_from_database(user_message)
                
                final_prompt = f"""
Contexto do Banco de Dados:
'{context_from_db if context_from_db else "Nenhum contexto específico do banco de dados."}'

Pergunta do Usuário:
'{user_message}'
"""
                
                response = self.chat_session.send_message(final_prompt)
                logger.info(f"Mensagem processada pelo Gemini: '{user_message[:50]}...'")
                
                return response.text, None
                
            except Exception as e:
                logger.error(f"Erro na API do Gemini: {e}. Usando resposta básica.")
                # Fallback para modo básico
                return self._basic_response(user_message), None
        
        # Modo básico (sem IA)
        else:
            logger.info(f"Mensagem processada em modo básico: '{user_message[:50]}...'")
            return self._basic_response(user_message), None
    
    def is_available(self):
        """
        Verifica se o chatbot está disponível.
        
        Returns:
            True (sempre disponível, mesmo em modo básico)
        """
        return True


# Instância global do serviço de chatbot
chatbot_service = ChatbotService()
