from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy import func, case

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
        
        from todoapp.models.task import Task
        pagination = Task.query.filter_by(user_id=current_user.id)\
            .order_by(Task.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('home.html', 
                             tasks=pagination.items, 
                             pagination=pagination,
                             current_time=datetime.utcnow())
    return render_template('landing.html')


@main.route("/account")
@login_required
def account():
    from todoapp.models.task import Task, TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED
    from todoapp.extensions import db
    
    stats = db.session.query(
        func.count(Task.id).label('total'),
        func.sum(case((Task.status == TASK_STATUS_PENDING, 1), else_=0)).label('pending'),
        func.sum(case((Task.status == TASK_STATUS_IN_PROGRESS, 1), else_=0)).label('in_progress'),
        func.sum(case((Task.status == TASK_STATUS_COMPLETED, 1), else_=0)).label('completed')
    ).filter(Task.user_id == current_user.id).first()
    
    return render_template('account.html',
                          title='个人资料',
                          total_tasks=stats.total or 0,
                          pending_tasks=stats.pending or 0,
                          in_progress_tasks=stats.in_progress or 0,
                          completed_tasks=stats.completed or 0)


@main.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    from todoapp.forms import TaskForm
    from todoapp.models.task import Task
    from todoapp.extensions import db
    
    form = TaskForm()
    
    if form.validate_on_submit():
        due_date = None
        if form.due_date.data:
            due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
        
        task = Task(
            title=form.title.data,
            content=form.content.data,
            due_date=due_date,
            priority=form.priority.data,
            author=current_user
        )
        db.session.add(task)
        db.session.commit()
        
        flash('任务已创建！', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('create_task.html', title='新任务', form=form, legend='创建新任务')


@main.route("/task/<int:task_id>")
@login_required
def task(task_id):
    from todoapp.models.task import Task
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限访问此任务', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('task.html', title=task.title, task=task, current_time=datetime.utcnow())


@main.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    from todoapp.models.task import Task
    from todoapp.forms import TaskForm
    from todoapp.extensions import db
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限修改此任务', 'danger')
        return redirect(url_for('main.home'))
    
    form = TaskForm()
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.content = form.content.data
        task.priority = form.priority.data
        
        if form.due_date.data:
            task.due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
        else:
            task.due_date = None
        
        db.session.commit()
        flash('任务已更新！', 'success')
        return redirect(url_for('main.task', task_id=task.id))
    
    elif request.method == 'GET':
        form.title.data = task.title
        form.content.data = task.content
        form.priority.data = task.priority
        if task.due_date:
            form.due_date.data = task.due_date.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('create_task.html', title='更新任务', form=form, legend='更新任务')


@main.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    from todoapp.models.task import Task
    from todoapp.extensions import db
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限删除此任务', 'danger')
        return redirect(url_for('main.home'))
    
    db.session.delete(task)
    db.session.commit()
    flash('任务已删除！', 'success')
    return redirect(url_for('main.home'))


@main.route("/task/<int:task_id>/status/<string:status>")
@login_required
def update_task_status(task_id, status):
    from todoapp.models.task import Task, TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED
    from todoapp.extensions import db
    
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限修改此任务', 'danger')
        return redirect(url_for('main.home'))
    
    valid_statuses = [TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED]
    if status not in valid_statuses:
        flash('无效的任务状态', 'danger')
        return redirect(url_for('main.home'))
    
    task.status = status
    if status == TASK_STATUS_COMPLETED:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    
    db.session.commit()
    flash(f'任务状态已更新！', 'success')
    return redirect(url_for('main.home'))


@main.route("/search")
@login_required
def search():
    from todoapp.models.task import Task
    
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    
    if query:
        tasks = Task.query.filter(
            Task.user_id == current_user.id,
            (Task.title.contains(query) | Task.content.contains(query))
        ).order_by(Task.created_at.desc())
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc())
    
    pagination = tasks.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('home.html',
                         tasks=pagination.items,
                         pagination=pagination,
                         current_time=datetime.utcnow(),
                         search_query=query)
