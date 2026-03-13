from flask import Blueprint, render_template, url_for, flash, redirect, request, session, current_app
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
import logging

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


def check_login_attempts(email):
    attempts_key = f'login_attempts_{email}'
    attempts = session.get(attempts_key, 0)
    max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
    window = current_app.config.get('LOGIN_ATTEMPT_WINDOW', 300)
    
    lockout_key = f'lockout_{email}'
    lockout_until = session.get(lockout_key)
    
    if lockout_until:
        lockout_time = datetime.fromisoformat(lockout_until)
        if datetime.utcnow() < lockout_time:
            remaining = (lockout_time - datetime.utcnow()).seconds
            return False, f'账户已锁定，请{remaining}秒后重试'
        else:
            session.pop(lockout_key, None)
            session.pop(attempts_key, None)
    
    return True, None


def record_failed_login(email):
    attempts_key = f'login_attempts_{email}'
    attempts = session.get(attempts_key, 0) + 1
    session[attempts_key] = attempts
    
    max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
    window = current_app.config.get('LOGIN_ATTEMPT_WINDOW', 300)
    
    if attempts >= max_attempts:
        lockout_key = f'lockout_{email}'
        lockout_until = datetime.utcnow() + timedelta(seconds=window)
        session[lockout_key] = lockout_until.isoformat()
        logger.warning(f'账户锁定: {email}, 尝试次数: {attempts}')
        return False, f'登录失败次数过多，账户已锁定{window}秒'
    
    return True, f'登录失败，还剩{max_attempts - attempts}次尝试机会'


def clear_login_attempts(email):
    attempts_key = f'login_attempts_{email}'
    lockout_key = f'lockout_{email}'
    session.pop(attempts_key, None)
    session.pop(lockout_key, None)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    from todoapp.forms import RegistrationForm
    form = RegistrationForm()
    
    if form.validate_on_submit():
        from todoapp.models.user import User
        from todoapp.extensions import db
        
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            logger.info(f'新用户注册成功: {user.email}')
            flash('您的账号已成功注册！现在可以登录了', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'注册失败: {str(e)}')
            flash('注册失败，请稍后重试', 'danger')
    
    return render_template('register.html', title='注册', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    from todoapp.forms import LoginForm
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        
        can_attempt, message = check_login_attempts(email)
        if not can_attempt:
            flash(message, 'danger')
            return render_template('login.html', title='登录', form=form)
        
        from todoapp.models.user import User
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(form.password.data):
            clear_login_attempts(email)
            login_user(user, remember=form.remember.data)
            
            logger.info(f'用户登录成功: {user.email}')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            can_continue, message = record_failed_login(email)
            logger.warning(f'登录失败: {email}, 原因: 用户名或密码错误')
            flash(message if message else '登录失败，请检查邮箱和密码', 'danger')
    
    return render_template('login.html', title='登录', form=form)


@auth.route('/logout')
@login_required
def logout():
    from flask_login import current_user
    logger.info(f'用户登出: {current_user.email}')
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('main.home'))
