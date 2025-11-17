"""
Constantes da aplicação PiFloor.

Este módulo centraliza todos os valores constantes usados na aplicação,
evitando magic numbers e strings hardcoded espalhadas pelo código.
"""
import os

# ===================================
# CONFIGURAÇÕES DE SEGURANÇA
# ===================================
MIN_PASSWORD_LENGTH = 6
MASTER_ADMIN_ID = 7

# ===================================
# CONFIGURAÇÕES DE CORS
# ===================================
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
ALLOWED_ORIGINS = [FRONTEND_URL]

# ===================================
# CONFIGURAÇÕES DE PAGINAÇÃO
# ===================================
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# ===================================
# CONFIGURAÇÕES DO CHATBOT
# ===================================
CHATBOT_MODEL_NAME = "models/gemini-2.5-flash"
CHATBOT_TEMPERATURE = 0.7
CHATBOT_MAX_TOKENS = 2048

CHATBOT_SYSTEM_PROMPT = """
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

# ===================================
# MENSAGENS DE ERRO PADRÃO
# ===================================
ERROR_MESSAGES = {
    'UNAUTHORIZED': 'Credenciais inválidas',
    'ACCOUNT_INACTIVE': 'Você foi inativado por condutas inadequadas, entre em contato com o suporte.',
    'ACCESS_DENIED_ADMIN': 'Acesso negado: apenas administradores',
    'ACCESS_DENIED_MASTER': 'Acesso negado: apenas o administrador master',
    'USER_NOT_FOUND': 'Usuário não encontrado',
    'PRODUCT_NOT_FOUND': 'Produto não encontrado',
    'MISSING_FIELDS': 'Campos obrigatórios não fornecidos',
    'USERNAME_EXISTS': 'Nome de usuário já existe',
    'EMAIL_EXISTS': 'E-mail já cadastrado',
    'PASSWORD_TOO_SHORT': f'A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres',
    'INVALID_PASSWORD': 'Senha atual incorreta',
    'CANNOT_DELETE_SELF': 'Você não pode excluir sua própria conta por esta rota',
    'CANNOT_MODIFY_SELF_STATUS': 'Você não pode alterar o próprio status',
    'ADMIN_CANNOT_DELETE': 'Contas de administrador não podem ser excluídas por esta rota',
}

# ===================================
# MENSAGENS DE SUCESSO PADRÃO
# ===================================
SUCCESS_MESSAGES = {
    'USER_CREATED': 'Usuário cadastrado com sucesso',
    'USER_UPDATED': 'Usuário atualizado com sucesso',
    'USER_DELETED': 'Usuário excluído com sucesso',
    'LOGIN_SUCCESS': 'Login bem-sucedido',
    'PASSWORD_CHANGED': 'Senha alterada com sucesso',
    'PRODUCT_CREATED': 'Produto criado com sucesso',
    'PRODUCT_UPDATED': 'Produto atualizado com sucesso',
    'PRODUCT_DELETED': 'Produto excluído com sucesso',
    'FAVORITE_ADDED': 'Produto adicionado aos favoritos',
    'FAVORITE_REMOVED': 'Produto removido dos favoritos',
    'REVIEW_SUBMITTED': 'Avaliação enviada com sucesso',
    'RATING_SUBMITTED': 'Nota registrada com sucesso',
}

# ===================================
# CÓDIGOS HTTP
# ===================================
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500
