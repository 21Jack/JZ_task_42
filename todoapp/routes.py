from flask import render_template, url_for, flash, redirect, request
from todoapp import app, db
from todoapp.forms import RegistrationForm, LoginForm, TaskForm
from todoapp.models import User, Task
from todoapp.models.task import TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

TASKS_PER_PAGE = 10

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        status_filter = request.args.get('status', '', type=str)
        sort_by = request.args.get('sort', 'created_at', type=str)
        order = request.args.get('order', 'desc', type=str)

        query = Task.query.filter_by(user_id=current_user.id)

        if search:
            query = query.filter(
                db.or_(
                    Task.title.contains(search),
                    Task.content.contains(search)
                )
            )

        if status_filter and status_filter in [TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED]:
            query = query.filter_by(status=status_filter)

        if sort_by == 'due_date':
            if order == 'asc':
                query = query.order_by(db.asc(db.case((Task.due_date.is_(None), 1), else_=0)), Task.due_date.asc())
            else:
                query = query.order_by(db.asc(db.case((Task.due_date.is_(None), 1), else_=0)), Task.due_date.desc())
        elif sort_by == 'title':
            query = query.order_by(Task.title.asc() if order == 'asc' else Task.title.desc())
        else:
            query = query.order_by(Task.created_at.desc() if order == 'desc' else Task.created_at.asc())

        tasks = query.paginate(page=page, per_page=TASKS_PER_PAGE)
        
        all_tasks = Task.query.filter_by(user_id=current_user.id).all()
        
        return render_template('home.html', 
                              tasks=tasks.items,
                              pagination=tasks,
                              current_time=datetime.utcnow(),
                              search=search,
                              status_filter=status_filter,
                              sort_by=sort_by,
                              order=order,
                              all_tasks=all_tasks)
    else:
        return render_template('landing.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('您的账号已成功注册！现在可以登录了', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('登录失败，请检查邮箱和密码', 'danger')
    return render_template('login.html', title='登录', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status=TASK_STATUS_PENDING).count()
    in_progress_tasks = Task.query.filter_by(user_id=current_user.id, status=TASK_STATUS_IN_PROGRESS).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status=TASK_STATUS_COMPLETED).count()
    
    return render_template('account.html', 
                          title='个人资料',
                          total_tasks=total_tasks,
                          pending_tasks=pending_tasks,
                          in_progress_tasks=in_progress_tasks,
                          completed_tasks=completed_tasks)


@app.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            content=form.content.data,
            due_date=form.due_date.data,
            author=current_user
        )
        db.session.add(task)
        db.session.commit()
        flash('任务已创建！', 'success')
        return redirect(url_for('home'))
    return render_template('create_task.html', title='新任务', form=form, legend='创建新任务')

@app.route("/task/<int:task_id>")
@login_required
def task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限访问此任务', 'danger')
        return redirect(url_for('home'))
    return render_template('task.html', title=task.title, task=task, current_time=datetime.utcnow())

@app.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限修改此任务', 'danger')
        return redirect(url_for('home'))
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.content = form.content.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash('任务已更新！', 'success')
        return redirect(url_for('task', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.content.data = task.content
        form.due_date.data = task.due_date
    return render_template('create_task.html', title='更新任务', form=form, legend='更新任务')

@app.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限删除此任务', 'danger')
        return redirect(url_for('home'))
    db.session.delete(task)
    db.session.commit()
    flash('任务已删除！', 'success')
    return redirect(url_for('home'))

@app.route("/task/<int:task_id>/status/<string:status>", methods=['POST'])
@login_required
def update_task_status(task_id, status):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限修改此任务', 'danger')
        return redirect(url_for('home'))
    
    valid_statuses = [TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED]
    if status not in valid_statuses:
        flash('无效的任务状态', 'danger')
        return redirect(url_for('home'))
    
    task.status = status
    if status == TASK_STATUS_COMPLETED:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    
    db.session.commit()
    status_names = {'pending': '待处理', 'in_progress': '进行中', 'completed': '已完成'}
    flash(f'任务状态已更新为 {status_names.get(status, status)}！', 'success')
    return redirect(url_for('home'))
