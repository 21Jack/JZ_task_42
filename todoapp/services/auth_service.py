"""
认证服务层
处理用户认证相关的业务逻辑
"""
import logging
from flask_login import login_user as flask_login_user, logout_user as flask_logout_user
from todoapp.repositories.user_repository import UserRepository
from todoapp.utils.validators import validate_password_strength

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def register(username, email, password):
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            (user, error_message) 元组
        """
        try:
            # 验证用户名
            if UserRepository.username_exists(username):
                return None, '该用户名已被使用'
            
            # 验证邮箱
            if UserRepository.email_exists(email):
                return None, '该邮箱已被注册'
            
            # 验证密码强度
            is_valid, error_msg = validate_password_strength(password)
            if not is_valid:
                return None, error_msg
            
            # 创建用户
            user = UserRepository.create(username, email, password)
            logger.info(f'用户注册成功: {email}')
            return user, None
            
        except Exception as e:
            logger.error(f'用户注册失败: {e}', exc_info=True)
            return None, '注册失败，请稍后重试'
    
    @staticmethod
    def login(email, password, remember=False):
        """
        用户登录
        
        Args:
            email: 邮箱
            password: 密码
            remember: 是否记住登录
            
        Returns:
            (user, error_message) 元组
        """
        try:
            # 查找用户
            user = UserRepository.get_by_email(email)
            
            if not user:
                logger.warning(f'登录失败: 用户不存在 - {email}')
                return None, '邮箱或密码错误'
            
            # 验证密码
            if not user.check_password(password):
                logger.warning(f'登录失败: 密码错误 - {email}')
                return None, '邮箱或密码错误'
            
            # 执行登录
            flask_login_user(user, remember=remember)
            logger.info(f'用户登录成功: {email}')
            return user, None
            
        except Exception as e:
            logger.error(f'用户登录失败: {e}', exc_info=True)
            return None, '登录失败，请稍后重试'
    
    @staticmethod
    def logout():
        """用户登出"""
        try:
            flask_logout_user()
            logger.info('用户登出')
            return True
        except Exception as e:
            logger.error(f'用户登出失败: {e}', exc_info=True)
            return False
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        修改密码
        
        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (success, error_message) 元组
        """
        try:
            # 验证旧密码
            if not user.check_password(old_password):
                return False, '当前密码错误'
            
            # 验证新密码强度
            is_valid, error_msg = validate_password_strength(new_password)
            if not is_valid:
                return False, error_msg
            
            # 更新密码
            user.set_password(new_password)
            from todoapp.extensions import db
            db.session.commit()
            
            logger.info(f'用户修改密码成功: {user.email}')
            return True, None
            
        except Exception as e:
            logger.error(f'修改密码失败: {e}', exc_info=True)
            return False, '修改密码失败，请稍后重试'
