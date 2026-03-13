"""
任务数据访问层
封装所有任务相关的数据库操作
"""
from sqlalchemy import desc, asc
from todoapp.extensions import db
from todoapp.models.task import Task, TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED


class TaskRepository:
    """任务仓库类"""
    
    @staticmethod
    def get_by_id(task_id):
        """通过ID获取任务"""
        return Task.query.get(task_id)
    
    @staticmethod
    def get_by_id_and_user(task_id, user_id):
        """通过ID和用户ID获取任务（权限验证）"""
        return Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    @staticmethod
    def get_all_by_user(user_id, page=None, per_page=None, status=None, order_by='created_at', order_desc=True):
        """
        获取用户的所有任务
        
        Args:
            user_id: 用户ID
            page: 页码（分页时）
            per_page: 每页数量
            status: 状态筛选
            order_by: 排序字段
            order_desc: 是否降序
        """
        query = Task.query.filter_by(user_id=user_id)
        
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 排序
        order_column = getattr(Task, order_by, Task.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # 分页
        if page and per_page:
            return query.paginate(page=page, per_page=per_page, error_out=False)
        
        return query.all()
    
    @staticmethod
    def get_overdue_tasks(user_id, current_time):
        """获取用户的过期任务"""
        return Task.query.filter(
            Task.user_id == user_id,
            Task.due_date < current_time,
            Task.status != TASK_STATUS_COMPLETED
        ).all()
    
    @staticmethod
    def get_upcoming_tasks(user_id, current_time, limit=5):
        """获取即将到期的任务"""
        return Task.query.filter(
            Task.user_id == user_id,
            Task.due_date >= current_time,
            Task.status != TASK_STATUS_COMPLETED
        ).order_by(asc(Task.due_date)).limit(limit).all()
    
    @staticmethod
    def create(title, content, user_id, due_date=None, status=TASK_STATUS_PENDING):
        """创建新任务"""
        task = Task(
            title=title.strip(),
            content=content.strip(),
            user_id=user_id,
            due_date=due_date,
            status=status
        )
        db.session.add(task)
        db.session.commit()
        return task
    
    @staticmethod
    def update(task, **kwargs):
        """更新任务"""
        for key, value in kwargs.items():
            if hasattr(task, key):
                if key in ['title', 'content'] and value:
                    value = value.strip()
                setattr(task, key, value)
        db.session.commit()
        return task
    
    @staticmethod
    def update_status(task, status):
        """更新任务状态"""
        from datetime import datetime
        
        task.status = status
        if status == TASK_STATUS_COMPLETED:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        db.session.commit()
        return task
    
    @staticmethod
    def delete(task):
        """删除任务"""
        db.session.delete(task)
        db.session.commit()
    
    @staticmethod
    def get_task_stats(user_id):
        """获取任务统计信息"""
        from sqlalchemy import func
        
        stats = db.session.query(
            Task.status,
            func.count(Task.id)
        ).filter_by(user_id=user_id).group_by(Task.status).all()
        
        result = {
            'total': 0,
            'pending': 0,
            'in_progress': 0,
            'completed': 0
        }
        
        for status, count in stats:
            result[status] = count
            result['total'] += count
        
        return result
    
    @staticmethod
    def search(user_id, keyword, page=1, per_page=10):
        """搜索任务"""
        query = Task.query.filter(
            Task.user_id == user_id,
            db.or_(
                Task.title.ilike(f'%{keyword}%'),
                Task.content.ilike(f'%{keyword}%')
            )
        ).order_by(desc(Task.created_at))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
