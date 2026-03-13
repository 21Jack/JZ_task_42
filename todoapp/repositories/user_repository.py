"""
用户数据访问层
封装所有用户相关的数据库操作
"""
from todoapp.extensions import db
from todoapp.models.user import User


class UserRepository:
    """用户仓库类"""
    
    @staticmethod
    def get_by_id(user_id):
        """通过ID获取用户"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email):
        """通过邮箱获取用户"""
        return User.query.filter_by(email=email.lower().strip()).first()
    
    @staticmethod
    def get_by_username(username):
        """通过用户名获取用户"""
        return User.query.filter_by(username=username.lower().strip()).first()
    
    @staticmethod
    def email_exists(email):
        """检查邮箱是否已存在"""
        return User.query.filter_by(email=email.lower().strip()).first() is not None
    
    @staticmethod
    def username_exists(username):
        """检查用户名是否已存在"""
        return User.query.filter_by(username=username.lower().strip()).first() is not None
    
    @staticmethod
    def create(username, email, password):
        """创建新用户"""
        user = User(
            username=username.strip(),
            email=email.lower().strip()
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update(user, **kwargs):
        """更新用户信息"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user):
        """删除用户"""
        db.session.delete(user)
        db.session.commit()
    
    @staticmethod
    def get_task_stats(user_id):
        """获取用户任务统计"""
        from todoapp.models.task import Task, TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED
        
        tasks = Task.query.filter_by(user_id=user_id).all()
        return {
            'total': len(tasks),
            'pending': len([t for t in tasks if t.status == TASK_STATUS_PENDING]),
            'in_progress': len([t for t in tasks if t.status == TASK_STATUS_IN_PROGRESS]),
            'completed': len([t for t in tasks if t.status == TASK_STATUS_COMPLETED])
        }
