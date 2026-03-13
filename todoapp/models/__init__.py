"""
模型包初始化
"""
from todoapp.models.user import User
from todoapp.models.task import Task, TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED

__all__ = ['User', 'Task', 'TASK_STATUS_PENDING', 'TASK_STATUS_IN_PROGRESS', 'TASK_STATUS_COMPLETED']
