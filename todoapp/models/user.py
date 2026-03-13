from todoapp.extensions import db
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
import re


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    tasks = db.relationship('Task', backref='author', lazy=True, cascade='all, delete-orphan')
    
    @staticmethod
    def validate_password_strength(password):
        if len(password) < 8:
            return False, '密码长度至少8位'
        if not re.search(r'[A-Z]', password):
            return False, '密码需包含大写字母'
        if not re.search(r'[a-z]', password):
            return False, '密码需包含小写字母'
        if not re.search(r'\d', password):
            return False, '密码需包含数字'
        return True, '密码强度符合要求'
    
    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)
    
    def check_password(self, password):
        try:
            return pbkdf2_sha256.verify(password, self.password_hash)
        except Exception:
            return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
