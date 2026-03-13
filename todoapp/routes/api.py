from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime

api = Blueprint('api', __name__)


@api.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    from todoapp.models.task import Task
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    
    pagination = query.order_by(Task.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    tasks = [{
        'id': task.id,
        'title': task.title,
        'content': task.content,
        'status': task.status,
        'priority': task.priority,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None
    } for task in pagination.items]
    
    return jsonify({
        'tasks': tasks,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@api.route('/tasks', methods=['POST'])
@login_required
def create_task():
    from todoapp.models.task import Task
    from todoapp.extensions import db
    
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': '标题不能为空'}), 400
    
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'error': '日期格式无效'}), 400
    
    task = Task(
        title=data['title'],
        content=data.get('content', ''),
        due_date=due_date,
        priority=data.get('priority', 'medium'),
        author=current_user
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'message': '任务创建成功'
    }), 201


@api.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    from todoapp.models.task import Task
    from todoapp.extensions import db
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        return jsonify({'error': '无权限'}), 403
    
    data = request.get_json()
    
    if data.get('title'):
        task.title = data['title']
    if 'content' in data:
        task.content = data['content']
    if 'status' in data:
        task.status = data['status']
        if data['status'] == 'completed':
            task.completed_at = datetime.utcnow()
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    
    db.session.commit()
    
    return jsonify({'message': '任务更新成功'})


@api.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    from todoapp.models.task import Task
    from todoapp.extensions import db
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        return jsonify({'error': '无权限'}), 403
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': '任务删除成功'})


@api.route('/tasks/<int:task_id>/status', methods=['PATCH'])
@login_required
def update_status(task_id):
    from todoapp.models.task import Task, TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED
    from todoapp.extensions import db
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        return jsonify({'error': '无权限'}), 403
    
    data = request.get_json()
    status = data.get('status')
    
    valid_statuses = [TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED]
    if status not in valid_statuses:
        return jsonify({'error': '无效的状态'}), 400
    
    task.status = status
    if status == TASK_STATUS_COMPLETED:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    
    db.session.commit()
    
    return jsonify({'message': '状态更新成功', 'status': status})


@api.route('/stats', methods=['GET'])
@login_required
def get_stats():
    from todoapp.models.task import Task
    from sqlalchemy import func
    from todoapp.extensions import db
    
    stats = db.session.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(Task.user_id == current_user.id).group_by(Task.status).all()
    
    return jsonify({
        'stats': [{'status': s[0], 'count': s[1]} for s in stats]
    })
