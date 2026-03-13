from flask import render_template, url_for, flash, redirect, request
from todoapp import app, db
from todoapp.forms import RegistrationForm, LoginForm, TaskForm
from todoapp.models import User, Task
from todoapp.models.task import TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_COMPLETED
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
    """主页路由，根据用户是否登录显示不同内容"""
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
        return render_template('home.html', tasks=tasks, current_time=datetime.utcnow())
    else:
        return render_template('landing.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """用户注册路由"""
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
    """用户登录路由"""
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
    """用户个人资料路由，显示用户任务统计信息"""
    # 获取用户的所有任务
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    # 计算任务统计数据
    total_tasks = len(tasks)
    pending_tasks = len([task for task in tasks if task.status == TASK_STATUS_PENDING])
    in_progress_tasks = len([task for task in tasks if task.status == TASK_STATUS_IN_PROGRESS])
    completed_tasks = len([task for task in tasks if task.status == TASK_STATUS_COMPLETED])
    
    return render_template('account.html', 
                          title='个人资料',
                          total_tasks=total_tasks,
                          pending_tasks=pending_tasks,
                          in_progress_tasks=in_progress_tasks,
                          completed_tasks=completed_tasks)


@app.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    """创建新任务路由"""
    form = TaskForm()
    if form.validate_on_submit():
        # 解析日期时间字符串
        due_date = None
        if form.due_date.data:
            due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
        
        task = Task(
            title=form.title.data,
            content=form.content.data,
            due_date=due_date,
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
    """查看单个任务详情的路由"""
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限访问此任务', 'danger')
        return redirect(url_for('home'))
    return render_template('task.html', title=task.title, task=task, current_time=datetime.utcnow())

@app.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    """更新任务的路由"""
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限修改此任务', 'danger')
        return redirect(url_for('home'))
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.content = form.content.data
        
        # 解析日期时间字符串
        if form.due_date.data:
            task.due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
        else:
            task.due_date = None
            
        db.session.commit()
        flash('任务已更新！', 'success')
        return redirect(url_for('task', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.content.data = task.content
        # 将datetime对象转换为表单需要的字符串格式
        if task.due_date:
            form.due_date.data = task.due_date.strftime('%Y-%m-%dT%H:%M')
    return render_template('create_task.html', title='更新任务', form=form, legend='更新任务')

@app.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    """删除任务的路由"""
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限删除此任务', 'danger')
        return redirect(url_for('home'))
    db.session.delete(task)
    db.session.commit()
    flash('任务已删除！', 'success')
    return redirect(url_for('home'))

@app.route("/task/<int:task_id>/status/<string:status>")
@login_required
def update_task_status(task_id, status):
    """更新任务状态"""
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('您没有权限修改此任务', 'danger')
        return redirect(url_for('home'))
    
    # 验证状态值是否有效
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
    flash(f'任务状态已更新为 {status}！', 'success')
    return redirect(url_for('home'))
