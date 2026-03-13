"""
任务模型模块
"""
from datetime import datetime
from todoapp.extensions import db

# 任务状态常量
TASK_STATUS_PENDING = 'pending'          # 待处理
TASK_STATUS_IN_PROGRESS = 'in_progress'  # 进行中
TASK_STATUS_COMPLETED = 'completed'      # 已完成


class Task(db.Model):
    """任务模型类"""
    __tablename__ = 'tasks'
    
    # 主键和基本信息字段
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=TASK_STATUS_PENDING, index=True)
    
    # 时间相关字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # 外键关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    def is_overdue(self, current_time=None):
        """检查任务是否已过期"""
        if not self.due_date or self.status == TASK_STATUS_COMPLETED:
            return False
        
        if not current_time:
            current_time = datetime.utcnow()
            
        return self.due_date < current_time
    
    def get_status_display(self):
        """获取任务状态的中文显示名称"""
        status_map = {
            TASK_STATUS_PENDING: '待处理',
            TASK_STATUS_IN_PROGRESS: '进行中',
            TASK_STATUS_COMPLETED: '已完成'
        }
        return status_map.get(self.status, self.status)
    
    def get_status_color(self):
        """获取状态对应的颜色类"""
        color_map = {
            TASK_STATUS_PENDING: 'info',
            TASK_STATUS_IN_PROGRESS: 'warning',
            TASK_STATUS_COMPLETED: 'success'
        }
        return color_map.get(self.status, 'secondary')
    
    def can_transition_to(self, new_status):
        """检查状态转换是否合法"""
        transitions = {
            TASK_STATUS_PENDING: [TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED],
            TASK_STATUS_IN_PROGRESS: [TASK_STATUS_PENDING, TASK_STATUS_COMPLETED],
            TASK_STATUS_COMPLETED: [TASK_STATUS_PENDING]
        }
        return new_status in transitions.get(self.status, [])
    
    def to_dict(self):
        """将任务对象转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'status_display': self.get_status_display(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_overdue': self.is_overdue(),
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f"Task('{self.title}', '{self.status}', '{self.created_at}')"
