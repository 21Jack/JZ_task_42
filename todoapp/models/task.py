from todoapp.extensions import db
from datetime import datetime

TASK_STATUS_PENDING = 'pending'
TASK_STATUS_IN_PROGRESS = 'in_progress'
TASK_STATUS_COMPLETED = 'completed'

TASK_PRIORITY_LOW = 'low'
TASK_PRIORITY_MEDIUM = 'medium'
TASK_PRIORITY_HIGH = 'high'


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=TASK_STATUS_PENDING)
    priority = db.Column(db.String(20), nullable=False, default=TASK_PRIORITY_MEDIUM)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def is_overdue(self, current_time=None):
        if not self.due_date or self.status == TASK_STATUS_COMPLETED:
            return False
        if not current_time:
            current_time = datetime.utcnow()
        return self.due_date < current_time
    
    def get_status_display(self):
        status_map = {
            TASK_STATUS_PENDING: '待处理',
            TASK_STATUS_IN_PROGRESS: '进行中',
            TASK_STATUS_COMPLETED: '已完成'
        }
        return status_map.get(self.status, self.status)
    
    def get_priority_display(self):
        priority_map = {
            TASK_PRIORITY_LOW: '低',
            TASK_PRIORITY_MEDIUM: '中',
            TASK_PRIORITY_HIGH: '高'
        }
        return priority_map.get(self.priority, self.priority)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f"Task('{self.title}', '{self.status}', '{self.priority}')"
