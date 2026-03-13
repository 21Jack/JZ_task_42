"""
验证工具模块
提供各种验证函数
"""
import re


def validate_password_strength(password):
    """
    验证密码强度
    
    要求：
    - 至少8位
    - 包含至少一个大写字母
    - 包含至少一个小写字母
    - 包含至少一个数字
    - 包含至少一个特殊字符
    
    Args:
        password: 密码字符串
        
    Returns:
        (is_valid, error_message) 元组
    """
    if not password:
        return False, '密码不能为空'
    
    if len(password) < 8:
        return False, '密码长度至少为8位'
    
    if not re.search(r'[A-Z]', password):
        return False, '密码必须包含至少一个大写字母'
    
    if not re.search(r'[a-z]', password):
        return False, '密码必须包含至少一个小写字母'
    
    if not re.search(r'\d', password):
        return False, '密码必须包含至少一个数字'
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, '密码必须包含至少一个特殊字符 (!@#$%^&*(),.?":{}|<>)'
    
    return True, None


def validate_username(username):
    """
    验证用户名
    
    要求：
    - 2-20个字符
    - 只能包含字母、数字、下划线
    - 必须以字母开头
    
    Args:
        username: 用户名字符串
        
    Returns:
        (is_valid, error_message) 元组
    """
    if not username:
        return False, '用户名不能为空'
    
    if len(username) < 2 or len(username) > 20:
        return False, '用户名长度必须在2-20个字符之间'
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, '用户名必须以字母开头，只能包含字母、数字和下划线'
    
    return True, None


def sanitize_html(text):
    """
    清理HTML标签，防止XSS攻击
    
    Args:
        text: 输入文本
        
    Returns:
        清理后的文本
    """
    import bleach
    
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']
    allowed_attrs = {}
    
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def truncate_text(text, max_length=100, suffix='...'):
    """
    截断文本
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + suffix
