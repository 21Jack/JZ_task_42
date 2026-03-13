"""
应用配置文件
包含Flask应用程序的所有配置项
"""
import os

# 安全密钥，用于会话管理、CSRF保护等
# 生产环境中应从环境变量获取，这里提供了一个默认值用于开发和测试
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

# 数据库配置
# 当前使用SQLite数据库进行测试和开发
# 数据库文件将保存在应用程序目录下，文件名为todolist.db
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'todolist.db')

# 禁用SQLAlchemy的跟踪修改功能，以提高性能
SQLALCHEMY_TRACK_MODIFICATIONS = False
