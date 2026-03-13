"""
认证路由模块
处理用户注册、登录、登出等
"""
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required

from todoapp.services.auth_service import AuthService
from todoapp.forms import RegistrationForm, LoginForm, ChangePasswordForm
from todoapp.extensions import limiter

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """用户注册路由"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user, error = AuthService.register(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if user:
            flash('注册成功！请登录', 'success')
            logger.info(f'新用户注册: {form.email.data}')
            return redirect(url_for('auth.login'))
        else:
            flash(error or '注册失败', 'danger')
            logger.warning(f'注册失败: {form.email.data} - {error}')
    
    return render_template('auth/register.html', form=form, title='注册')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """用户登录路由"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        logger.info(f'尝试登录: {form.email.data}')
        
        user, error = AuthService.login(
            email=form.email.data,
            password=form.password.data,
            remember=form.remember.data
        )
        
        if user:
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            
            # 安全检查：防止开放重定向攻击
            if next_page and not next_page.startswith('/'):
                next_page = None
            
            logger.info(f'用户登录成功: {form.email.data}')
            return redirect(next_page or url_for('main.home'))
        else:
            flash(error or '登录失败', 'danger')
            logger.warning(f'登录失败: {form.email.data} - {error}')
    elif request.method == 'POST' and not form.validate():
        # 表单验证失败
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
        logger.warning(f'登录表单验证失败: {form.errors}')
    
    return render_template('auth/login.html', form=form, title='登录')


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出路由"""
    AuthService.logout()
    flash('您已成功登出', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/account')
@login_required
def account():
    """用户账户页面"""
    from todoapp.services.task_service import TaskService
    
    stats = TaskService.get_task_stats(current_user.id)
    
    return render_template('auth/account.html',
                         title='个人资料',
                         stats=stats)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码路由"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        success, error = AuthService.change_password(
            user=current_user,
            old_password=form.old_password.data,
            new_password=form.new_password.data
        )
        
        if success:
            flash('密码修改成功！', 'success')
            return redirect(url_for('auth.account'))
        else:
            flash(error or '密码修改失败', 'danger')
    
    return render_template('auth/change_password.html', form=form, title='修改密码')


# API端点
@auth_bp.route('/api/check-email', methods=['POST'])
def check_email():
    """检查邮箱是否可用"""
    from todoapp.repositories.user_repository import UserRepository
    
    email = request.json.get('email', '').strip().lower()
    if not email:
        return jsonify({'available': False, 'error': '邮箱不能为空'})
    
    available = not UserRepository.email_exists(email)
    return jsonify({'available': available})


@auth_bp.route('/api/check-username', methods=['POST'])
def check_username():
    """检查用户名是否可用"""
    from todoapp.repositories.user_repository import UserRepository
    
    username = request.json.get('username', '').strip()
    if not username:
        return jsonify({'available': False, 'error': '用户名不能为空'})
    
    available = not UserRepository.username_exists(username)
    return jsonify({'available': available})
