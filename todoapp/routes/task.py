"""
任务路由模块
处理任务的CRUD操作
"""
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required

from todoapp.services.task_service import TaskService
from todoapp.forms import TaskForm
from todoapp.extensions import limiter

logger = logging.getLogger(__name__)
task_bp = Blueprint('task', __name__)


@task_bp.route('/list')
@login_required
def list_tasks():
    """任务列表页面"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', None)
    per_page = 10
    
    pagination = TaskService.get_user_tasks(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        status=status
    )
    
    stats = TaskService.get_task_stats(current_user.id)
    
    return render_template('task/list.html',
                         tasks=pagination.items,
                         pagination=pagination,
                         stats=stats,
                         current_status=status,
                         current_time=datetime.utcnow(),
                         title='我的任务')


@task_bp.route('/new', methods=['GET', 'POST'])
@login_required
@limiter.limit("30 per minute")
def new_task():
    """创建新任务"""
    form = TaskForm()
    
    if form.validate_on_submit():
        # 解析截止日期
        due_date = None
        if form.due_date.data:
            try:
                due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('无效的日期格式', 'danger')
                return render_template('task/form.html', form=form, title='新建任务', legend='创建新任务')
        
        task, error = TaskService.create_task(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            due_date=due_date
        )
        
        if task:
            flash('任务创建成功！', 'success')
            return redirect(url_for('task.list_tasks'))
        else:
            flash(error or '任务创建失败', 'danger')
    
    return render_template('task/form.html', form=form, title='新建任务', legend='创建新任务')


@task_bp.route('/<int:task_id>')
@login_required
def view_task(task_id):
    """查看任务详情"""
    task, error = TaskService.get_task(task_id, current_user.id)
    
    if not task:
        flash(error or '任务不存在', 'danger')
        return redirect(url_for('task.list_tasks'))
    
    return render_template('task/detail.html',
                         task=task,
                         current_time=datetime.utcnow(),
                         title=task.title)


@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@limiter.limit("30 per minute")
def edit_task(task_id):
    """编辑任务"""
    task, error = TaskService.get_task(task_id, current_user.id)
    
    if not task:
        flash(error or '任务不存在', 'danger')
        return redirect(url_for('task.list_tasks'))
    
    form = TaskForm()
    
    if form.validate_on_submit():
        # 解析截止日期
        due_date = None
        if form.due_date.data:
            try:
                due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('无效的日期格式', 'danger')
                return render_template('task/form.html', form=form, title='编辑任务', legend='编辑任务')
        
        task, error = TaskService.update_task(
            task_id=task_id,
            user_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            due_date=due_date
        )
        
        if task:
            flash('任务更新成功！', 'success')
            return redirect(url_for('task.view_task', task_id=task.id))
        else:
            flash(error or '任务更新失败', 'danger')
    
    elif request.method == 'GET':
        form.title.data = task.title
        form.content.data = task.content
        if task.due_date:
            form.due_date.data = task.due_date.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('task/form.html', form=form, title='编辑任务', legend='编辑任务')


@task_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
@limiter.limit("20 per minute")
def delete_task(task_id):
    """删除任务"""
    success, error = TaskService.delete_task(task_id, current_user.id)
    
    if success:
        flash('任务已删除', 'success')
    else:
        flash(error or '删除失败', 'danger')
    
    return redirect(url_for('task.list_tasks'))


@task_bp.route('/<int:task_id>/status', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def update_status(task_id):
    """更新任务状态（AJAX）"""
    status = request.json.get('status')
    
    if not status:
        return jsonify({'success': False, 'error': '缺少状态参数'}), 400
    
    task, error = TaskService.update_task_status(task_id, current_user.id, status)
    
    if task:
        return jsonify({
            'success': True,
            'task': {
                'id': task.id,
                'status': task.status,
                'status_display': task.get_status_display(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
        })
    else:
        return jsonify({'success': False, 'error': error}), 400


@task_bp.route('/search')
@login_required
def search():
    """搜索任务"""
    keyword = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not keyword:
        flash('请输入搜索关键词', 'warning')
        return redirect(url_for('task.list_tasks'))
    
    pagination = TaskService.search_tasks(
        user_id=current_user.id,
        keyword=keyword,
        page=page,
        per_page=10
    )
    
    return render_template('task/search.html',
                         tasks=pagination.items if pagination else [],
                         pagination=pagination,
                         keyword=keyword,
                         title=f'搜索: {keyword}')
