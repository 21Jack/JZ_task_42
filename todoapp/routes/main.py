"""
主页面路由模块
处理首页、关于页面等
"""
from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from todoapp.services.task_service import TaskService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/home')
def home():
    """首页路由"""
    if current_user.is_authenticated:
        # 获取任务统计
        stats = TaskService.get_task_stats(current_user.id)
        
        # 获取最近任务（分页）
        page = 1
        per_page = 10
        pagination = TaskService.get_user_tasks(
            user_id=current_user.id,
            page=page,
            per_page=per_page
        )
        
        return render_template('home.html',
                             tasks=pagination.items,
                             pagination=pagination,
                             stats=stats,
                             current_time=datetime.utcnow())
    else:
        return render_template('landing.html')


@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘"""
    from datetime import datetime, timedelta
    
    # 获取任务统计
    stats = TaskService.get_task_stats(current_user.id)
    
    # 获取即将到期的任务
    upcoming_tasks = TaskService.get_user_tasks(
        user_id=current_user.id,
        page=1,
        per_page=5
    )
    
    return render_template('dashboard.html',
                         stats=stats,
                         upcoming_tasks=upcoming_tasks.items,
                         current_time=datetime.utcnow())
