# 任务模型模块
from todoapp import db
from datetime import datetime


# 任务状态常量
TASK_STATUS_PENDING = 'pending'      # 待处理
TASK_STATUS_IN_PROGRESS = 'in_progress'  # 进行中
TASK_STATUS_COMPLETED = 'completed'    # 已完成


class Task(db.Model):
    """任务模型类，继承自db.Model"""
    # 表名
    __tablename__ = 'tasks'
    
    # 主键和基本信息字段
    id = db.Column(db.Integer, primary_key=True)  # 任务ID，主键
    title = db.Column(db.String(100), nullable=False)  # 任务标题，非空
    content = db.Column(db.Text, nullable=False)  # 任务内容，非空
    status = db.Column(db.String(20), nullable=False, default=TASK_STATUS_PENDING)  # 任务状态
    
    # 时间相关字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 创建时间
    due_date = db.Column(db.DateTime, nullable=True)  # 截止日期（可选）
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间（可选）
    
    # 外键关联
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 所属用户ID
    
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
    
    def __repr__(self):
        """任务对象的字符串表示"""
        return f"Task('{self.title}', '{self.status}', '{self.created_at}')"
