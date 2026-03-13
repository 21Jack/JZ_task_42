# 用户模型模块
from todoapp import db, login_manager
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256


@login_manager.user_loader
def load_user(user_id):
    """用户加载器函数，用于Flask-Login管理用户会话"""
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """用户模型类，继承自db.Model和UserMixin"""
    # 表名（可选，默认使用类名的小写形式）
    __tablename__ = 'user'
    
    # 主键和基本信息字段
    id = db.Column(db.Integer, primary_key=True)  # 用户ID，主键
    username = db.Column(db.String(20), unique=True, nullable=False)  # 用户名，唯一且非空
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱，唯一且非空
    password_hash = db.Column(db.String(128), nullable=False)  # 密码哈希值，非空
    
    # 与Task模型的一对多关系
    tasks = db.relationship('Task', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置用户密码（哈希处理）"""
        self.password_hash = pbkdf2_sha256.hash(password)
    
    def check_password(self, password):
        """验证用户密码"""
        return pbkdf2_sha256.verify(password, self.password_hash)
    
    def __repr__(self):
        """用户对象的字符串表示"""
        return f"User('{self.username}', '{self.email}')"
