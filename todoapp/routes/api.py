"""
API路由模块
提供RESTful API接口
"""
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

from todoapp.services.task_service import TaskService
from todoapp.services.auth_service import AuthService
from todoapp.utils.decorators import api_response, require_ajax
from todoapp.extensions import limiter

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)


# 任务API
@api_bp.route('/tasks', methods=['GET'])
@login_required
@api_response
def get_tasks():
    """获取任务列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    # 限制每页最大数量
    per_page = min(per_page, 50)
    
    pagination = TaskService.get_user_tasks(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        status=status
    )
    
    return {
        'tasks': [task_to_dict(t) for t in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }


@api_bp.route('/tasks', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
@api_response
def create_task():
    """创建任务"""
    data = request.get_json()
    
    if not data:
        return {'error': '请求数据不能为空'}, 400
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    due_date_str = data.get('due_date')
    
    # 解析日期
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        except ValueError:
            return {'error': '无效的日期格式'}, 400
    
    task, error = TaskService.create_task(
        title=title,
        content=content,
        user_id=current_user.id,
        due_date=due_date
    )
    
    if task:
        return task_to_dict(task), 201
    else:
        return {'error': error}, 400


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
@api_response
def get_task(task_id):
    """获取单个任务"""
    task, error = TaskService.get_task(task_id, current_user.id)
    
    if task:
        return task_to_dict(task)
    else:
        return {'error': error}, 404


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
@limiter.limit("30 per minute")
@api_response
def update_task(task_id):
    """更新任务"""
    data = request.get_json()
    
    if not data:
        return {'error': '请求数据不能为空'}, 400
    
    # 构建更新参数
    update_data = {}
    if 'title' in data:
        update_data['title'] = data['title'].strip()
    if 'content' in data:
        update_data['content'] = data['content'].strip()
    if 'due_date' in data:
        if data['due_date']:
            try:
                update_data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return {'error': '无效的日期格式'}, 400
        else:
            update_data['due_date'] = None
    
    task, error = TaskService.update_task(task_id, current_user.id, **update_data)
    
    if task:
        return task_to_dict(task)
    else:
        return {'error': error}, 400


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
@limiter.limit("20 per minute")
@api_response
def delete_task(task_id):
    """删除任务"""
    success, error = TaskService.delete_task(task_id, current_user.id)
    
    if success:
        return {'message': '任务已删除'}, 200
    else:
        return {'error': error}, 400


@api_bp.route('/tasks/<int:task_id>/status', methods=['PATCH'])
@login_required
@limiter.limit("30 per minute")
@api_response
def patch_task_status(task_id):
    """更新任务状态"""
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return {'error': '缺少状态参数'}, 400
    
    task, error = TaskService.update_task_status(task_id, current_user.id, status)
    
    if task:
        return task_to_dict(task)
    else:
        return {'error': error}, 400


@api_bp.route('/tasks/stats', methods=['GET'])
@login_required
@api_response
def get_task_stats():
    """获取任务统计"""
    stats = TaskService.get_task_stats(current_user.id)
    return stats


@api_bp.route('/tasks/search', methods=['GET'])
@login_required
@api_response
def search_tasks():
    """搜索任务"""
    keyword = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not keyword:
        return {'error': '搜索关键词不能为空'}, 400
    
    per_page = min(per_page, 50)
    
    pagination = TaskService.search_tasks(
        user_id=current_user.id,
        keyword=keyword,
        page=page,
        per_page=per_page
    )
    
    if pagination:
        return {
            'tasks': [task_to_dict(t) for t in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    else:
        return {'tasks': [], 'pagination': {'total': 0}}


# 用户API
@api_bp.route('/user/profile', methods=['GET'])
@login_required
@api_response
def get_user_profile():
    """获取用户信息"""
    return {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'created_at': current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None
    }


@api_bp.route('/user/change-password', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
@api_response
def api_change_password():
    """修改密码"""
    data = request.get_json()
    
    if not data:
        return {'error': '请求数据不能为空'}, 400
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return {'error': '旧密码和新密码不能为空'}, 400
    
    success, error = AuthService.change_password(
        user=current_user,
        old_password=old_password,
        new_password=new_password
    )
    
    if success:
        return {'message': '密码修改成功'}
    else:
        return {'error': error}, 400


def task_to_dict(task):
    """将任务对象转换为字典"""
    return {
        'id': task.id,
        'title': task.title,
        'content': task.content,
        'status': task.status,
        'status_display': task.get_status_display(),
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'is_overdue': task.is_overdue(),
        'user_id': task.user_id
    }
