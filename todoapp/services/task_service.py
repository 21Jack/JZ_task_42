"""
任务服务层
处理任务相关的业务逻辑
"""
import logging
from datetime import datetime
from todoapp.repositories.task_repository import TaskRepository
from todoapp.models.task import TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类"""
    
    VALID_STATUSES = [TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED]
    
    @classmethod
    def create_task(cls, title, content, user_id, due_date=None):
        """
        创建任务
        
        Args:
            title: 任务标题
            content: 任务内容
            user_id: 用户ID
            due_date: 截止日期
            
        Returns:
            (task, error_message) 元组
        """
        try:
            # 验证输入
            if not title or not title.strip():
                return None, '任务标题不能为空'
            
            if not content or not content.strip():
                return None, '任务内容不能为空'
            
            # 验证截止日期
            if due_date and due_date < datetime.utcnow():
                return None, '截止日期不能早于当前时间'
            
            # 创建任务
            task = TaskRepository.create(
                title=title,
                content=content,
                user_id=user_id,
                due_date=due_date
            )
            
            logger.info(f'任务创建成功: {task.id} - 用户: {user_id}')
            return task, None
            
        except Exception as e:
            logger.error(f'任务创建失败: {e}', exc_info=True)
            return None, '任务创建失败，请稍后重试'
    
    @classmethod
    def update_task(cls, task_id, user_id, **kwargs):
        """
        更新任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID（权限验证）
            **kwargs: 要更新的字段
            
        Returns:
            (task, error_message) 元组
        """
        try:
            # 获取任务并验证权限
            task = TaskRepository.get_by_id_and_user(task_id, user_id)
            if not task:
                return None, '任务不存在或您没有权限修改'
            
            # 验证截止日期
            if 'due_date' in kwargs:
                due_date = kwargs['due_date']
                if due_date and due_date < datetime.utcnow():
                    return None, '截止日期不能早于当前时间'
            
            # 更新任务
            task = TaskRepository.update(task, **kwargs)
            logger.info(f'任务更新成功: {task_id}')
            return task, None
            
        except Exception as e:
            logger.error(f'任务更新失败: {e}', exc_info=True)
            return None, '任务更新失败，请稍后重试'
    
    @classmethod
    def update_task_status(cls, task_id, user_id, status):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            user_id: 用户ID（权限验证）
            status: 新状态
            
        Returns:
            (task, error_message) 元组
        """
        try:
            # 验证状态值
            if status not in cls.VALID_STATUSES:
                return None, '无效的任务状态'
            
            # 获取任务并验证权限
            task = TaskRepository.get_by_id_and_user(task_id, user_id)
            if not task:
                return None, '任务不存在或您没有权限修改'
            
            # 更新状态
            task = TaskRepository.update_status(task, status)
            logger.info(f'任务状态更新成功: {task_id} -> {status}')
            return task, None
            
        except Exception as e:
            logger.error(f'任务状态更新失败: {e}', exc_info=True)
            return None, '任务状态更新失败，请稍后重试'
    
    @classmethod
    def delete_task(cls, task_id, user_id):
        """
        删除任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID（权限验证）
            
        Returns:
            (success, error_message) 元组
        """
        try:
            # 获取任务并验证权限
            task = TaskRepository.get_by_id_and_user(task_id, user_id)
            if not task:
                return False, '任务不存在或您没有权限删除'
            
            # 删除任务
            TaskRepository.delete(task)
            logger.info(f'任务删除成功: {task_id}')
            return True, None
            
        except Exception as e:
            logger.error(f'任务删除失败: {e}', exc_info=True)
            return False, '任务删除失败，请稍后重试'
    
    @classmethod
    def get_task(cls, task_id, user_id):
        """
        获取单个任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID（权限验证）
            
        Returns:
            (task, error_message) 元组
        """
        task = TaskRepository.get_by_id_and_user(task_id, user_id)
        if not task:
            return None, '任务不存在或您没有权限访问'
        return task, None
    
    @classmethod
    def get_user_tasks(cls, user_id, page=1, per_page=10, status=None):
        """
        获取用户的任务列表
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            status: 状态筛选
            
        Returns:
            分页对象
        """
        return TaskRepository.get_all_by_user(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status
        )
    
    @classmethod
    def get_task_stats(cls, user_id):
        """获取用户任务统计"""
        return TaskRepository.get_task_stats(user_id)
    
    @classmethod
    def search_tasks(cls, user_id, keyword, page=1, per_page=10):
        """搜索任务"""
        if not keyword or not keyword.strip():
            return None
        return TaskRepository.search(user_id, keyword.strip(), page, per_page)
