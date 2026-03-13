"""
用户模型模块
"""
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from todoapp.extensions import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """用户模型类"""
    __tablename__ = 'users'
    
    # 主键和基本信息字段
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 时间戳字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 账户状态
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    
    # 与Task模型的一对多关系
    tasks = db.relationship('Task', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置用户密码（使用PBKDF2-SHA256哈希）"""
        self.password_hash = pbkdf2_sha256.hash(password, rounds=29000)
    
    def check_password(self, password):
        """验证用户密码"""
        try:
            return pbkdf2_sha256.verify(password, self.password_hash)
        except Exception:
            return False
    
    def get_id(self):
        """返回用户ID（Flask-Login要求）"""
        return str(self.id)
    
    @property
    def task_count(self):
        """获取用户任务总数"""
        return self.tasks.count()
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'task_count': self.task_count
        }
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
