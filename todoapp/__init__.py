"""
TodoList应用工厂模块
使用应用工厂模式创建Flask应用实例
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from dotenv import load_dotenv

from todoapp.extensions import db, migrate, login_manager, limiter, csrf, init_extensions
from todoapp.config import config

# 加载环境变量
load_dotenv()


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置环境名称 (development/production/testing)
    
    Returns:
        Flask应用实例
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # 创建Flask应用
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    init_extensions(app)
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册模板过滤器
    register_template_filters(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app


def setup_logging(app):
    """配置日志系统"""
    if not app.debug:
        # 确保日志目录存在
        log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 文件日志处理器
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=10240,
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.info('TodoList应用启动')


def register_blueprints(app):
    """注册所有蓝图"""
    from todoapp.routes.main import main_bp
    from todoapp.routes.auth import auth_bp
    from todoapp.routes.task import task_bp
    from todoapp.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(task_bp, url_prefix='/task')
    app.register_blueprint(api_bp, url_prefix='/api')


def register_error_handlers(app):
    """注册错误处理器"""
    from flask import render_template, request, jsonify
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({'error': 'Bad Request', 'message': str(error.description)}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({'error': 'Forbidden', 'message': '您没有权限执行此操作'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'error': 'Not Found', 'message': '请求的资源不存在'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(429)
    def rate_limit_handler(error):
        if request.is_json:
            return jsonify({'error': 'Too Many Requests', 'message': '请求过于频繁，请稍后再试'}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}', exc_info=True)
        if request.is_json:
            return jsonify({'error': 'Internal Server Error', 'message': '服务器内部错误'}), 500
        return render_template('errors/500.html'), 500


def register_template_filters(app):
    """注册模板过滤器"""
    from datetime import datetime
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """格式化日期时间"""
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value.strftime(format)
    
    @app.template_filter('timeago')
    def timeago(value):
        """显示相对时间"""
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        
        now = datetime.utcnow()
        diff = now - value
        
        if diff.days > 365:
            return f'{diff.days // 365}年前'
        elif diff.days > 30:
            return f'{diff.days // 30}个月前'
        elif diff.days > 0:
            return f'{diff.days}天前'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600}小时前'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60}分钟前'
        else:
            return '刚刚'


# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    """加载用户回调函数"""
    from todoapp.models.user import User
    return User.query.get(int(user_id))
