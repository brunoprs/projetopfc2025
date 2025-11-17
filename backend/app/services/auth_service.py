"""
Serviço de autenticação e gerenciamento de usuários.

Este módulo contém a lógica de negócio relacionada a autenticação,
registro e gerenciamento de usuários.
"""
import logging
from flask_jwt_extended import create_access_token
from .. import db, bcrypt
from ..models import User, Favorite, Review
from ..constants import MIN_PASSWORD_LENGTH, ERROR_MESSAGES

logger = logging.getLogger(__name__)


class AuthService:
    """Serviço para gerenciar autenticação e usuários."""
    
    @staticmethod
    def register_user(username, email, password, name):
        """
        Registra um novo usuário no sistema.
        
        Args:
            username: Nome de usuário
            email: Email do usuário
            password: Senha em texto plano
            name: Nome completo
        
        Returns:
            Tupla (user, error_message)
            user será None se houver erro
        """
        # Validações
        if not all([username, email, password, name]):
            return None, ERROR_MESSAGES['MISSING_FIELDS']
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return None, ERROR_MESSAGES['PASSWORD_TOO_SHORT']
        
        email_lower = email.lower()
        
        # Verifica duplicatas
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email_lower)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return None, ERROR_MESSAGES['USERNAME_EXISTS']
            else:
                return None, ERROR_MESSAGES['EMAIL_EXISTS']
        
        # Cria usuário
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email_lower,
            password_hash=password_hash,
            name=name
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"Novo usuário registrado: {new_user.id} - {new_user.username}")
        return new_user, None
    
    @staticmethod
    def login_user(login_identifier, password):
        """
        Autentica um usuário e retorna token JWT.
        
        Args:
            login_identifier: Username ou email
            password: Senha em texto plano
        
        Returns:
            Tupla (token, user, error_message)
            token e user serão None se houver erro
        """
        if not login_identifier or not password:
            return None, None, ERROR_MESSAGES['MISSING_FIELDS']
        
        login_identifier_lower = login_identifier.lower()
        
        user = User.query.filter(
            (User.username.ilike(login_identifier_lower)) | 
            (User.email == login_identifier_lower)
        ).first()
        
        if not user:
            return None, None, ERROR_MESSAGES['UNAUTHORIZED']
        
        if not user.is_active:
            return None, None, ERROR_MESSAGES['ACCOUNT_INACTIVE']
        
        if not bcrypt.check_password_hash(user.password_hash, password):
            return None, None, ERROR_MESSAGES['UNAUTHORIZED']
        
        access_token = create_access_token(identity=str(user.id))
        logger.info(f"Login bem-sucedido: {user.id} - {user.username}")
        
        return access_token, user, None
    
    @staticmethod
    def create_admin_user(username, email, password, name):
        """
        Cria um novo usuário administrador.
        
        Args:
            username: Nome de usuário
            email: Email do usuário
            password: Senha em texto plano
            name: Nome completo
        
        Returns:
            Tupla (user, error_message)
        """
        # Validações
        if not all([username, email, password, name]):
            return None, ERROR_MESSAGES['MISSING_FIELDS']
        
        if len(password) < MIN_PASSWORD_LENGTH:
            return None, ERROR_MESSAGES['PASSWORD_TOO_SHORT']
        
        email_lower = email.lower()
        
        # Verifica duplicatas
        if User.query.filter((User.username == username) | (User.email == email_lower)).first():
            return None, 'Nome de usuário ou e-mail já estão em uso'
        
        try:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            new_admin = User(
                name=name,
                username=username,
                email=email_lower,
                password_hash=password_hash,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            
            logger.info(f"Novo admin criado: {new_admin.id} - {new_admin.username}")
            return new_admin, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar admin: {e}")
            return None, 'Erro interno ao criar administrador'
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """
        Atualiza dados de um usuário.
        
        Args:
            user_id: ID do usuário
            **kwargs: Campos a serem atualizados
        
        Returns:
            Tupla (user, error_message)
        """
        user = User.query.get(user_id)
        if not user:
            return None, ERROR_MESSAGES['USER_NOT_FOUND']
        
        # Atualiza apenas campos permitidos
        allowed_fields = ['name', 'username', 'email']
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)
        
        db.session.commit()
        logger.info(f"Usuário atualizado: {user.id} - {user.username}")
        return user, None
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Altera a senha de um usuário.
        
        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha
        
        Returns:
            Tupla (success, error_message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, ERROR_MESSAGES['USER_NOT_FOUND']
        
        if not current_password or not new_password:
            return False, ERROR_MESSAGES['MISSING_FIELDS']
        
        if not bcrypt.check_password_hash(user.password_hash, current_password):
            return False, ERROR_MESSAGES['INVALID_PASSWORD']
        
        if len(new_password) < MIN_PASSWORD_LENGTH:
            return False, ERROR_MESSAGES['PASSWORD_TOO_SHORT']
        
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        logger.info(f"Senha alterada: {user.id} - {user.username}")
        return True, None
    
    @staticmethod
    def delete_user(user_id, is_self_delete=False):
        """
        Exclui um usuário e suas dependências.
        
        Args:
            user_id: ID do usuário
            is_self_delete: Se é o próprio usuário excluindo sua conta
        
        Returns:
            Tupla (success, error_message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, ERROR_MESSAGES['USER_NOT_FOUND']
        
        if is_self_delete and user.is_admin:
            return False, ERROR_MESSAGES['ADMIN_CANNOT_DELETE']
        
        try:
            # Remove dependências
            Favorite.query.filter_by(user_id=user_id).delete()
            Review.query.filter_by(user_id=user_id).delete()
            
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"Usuário excluído: {user_id}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao excluir usuário: {e}")
            return False, 'Erro ao excluir usuário'
    
    @staticmethod
    def update_user_status(user_id, is_active):
        """
        Ativa ou inativa um usuário.
        
        Args:
            user_id: ID do usuário
            is_active: True para ativar, False para inativar
        
        Returns:
            Tupla (user, error_message)
        """
        user = User.query.get(user_id)
        if not user:
            return None, ERROR_MESSAGES['USER_NOT_FOUND']
        
        user.is_active = bool(is_active)
        db.session.commit()
        
        status = "ativado" if user.is_active else "inativado"
        logger.info(f"Usuário {status}: {user.id} - {user.username}")
        return user, None
