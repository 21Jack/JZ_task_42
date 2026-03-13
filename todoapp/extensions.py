"""
Flask扩展初始化模块
所有扩展都在这里初始化，避免循环导入
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# 数据库
db = SQLAlchemy()

# 数据库迁移
migrate = Migrate()

# 用户认证
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'info'

# 速率限制
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# CSRF保护
csrf = CSRFProtect()


def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
