"""
装饰器工具模块
提供各种装饰器函数
"""
import functools
import time
import logging
from flask import jsonify, request
from flask_login import current_user

logger = logging.getLogger(__name__)


def api_response(f):
    """
    API响应装饰器
    统一API响应格式
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            
            # 如果已经是Response对象，直接返回
            if hasattr(result, 'status_code'):
                return result
            
            # 统一成功响应格式
            if isinstance(result, tuple):
                data, status_code = result[0], result[1] if len(result) > 1 else 200
                return jsonify({
                    'success': True,
                    'data': data
                }), status_code
            
            return jsonify({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            logger.error(f'API错误: {e}', exc_info=True)
            return jsonify({
                'success': False,
                'error': '服务器内部错误',
                'message': str(e) if request.app.debug else '请稍后重试'
            }), 500
    
    return decorated_function


def log_execution_time(f):
    """
    记录函数执行时间装饰器
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # 毫秒
        logger.debug(f'{f.__name__} 执行时间: {execution_time:.2f}ms')
        
        return result
    
    return decorated_function


def require_ajax(f):
    """
    要求AJAX请求装饰器
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': '此接口仅接受AJAX请求'
            }), 400
        return f(*args, **kwargs)
    
    return decorated_function


def ownership_required(model_class, pk='id', user_field='user_id'):
    """
    资源所有权验证装饰器
    
    Args:
        model_class: 模型类
        pk: 主键字段名
        user_field: 用户ID字段名
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get(pk)
            if not resource_id:
                return jsonify({
                    'success': False,
                    'error': 'Bad Request',
                    'message': '缺少资源ID'
                }), 400
            
            resource = model_class.query.get(resource_id)
            if not resource:
                return jsonify({
                    'success': False,
                    'error': 'Not Found',
                    'message': '资源不存在'
                }), 404
            
            if getattr(resource, user_field) != current_user.id:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': '您没有权限操作此资源'
                }), 403
            
            # 将资源对象添加到kwargs
            kwargs['resource'] = resource
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
