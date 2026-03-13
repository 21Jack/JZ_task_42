"""
表单模块
定义所有WTForms表单类
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from datetime import datetime
import re

from todoapp.repositories.user_repository import UserRepository


class RegistrationForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=2, max=20, message='用户名长度必须在2-20个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, message='密码长度至少为8位')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')

    def validate_username(self, username):
        """验证用户名是否已存在"""
        if UserRepository.username_exists(username.data):
            raise ValidationError('该用户名已被使用，请选择其他用户名')
        
        # 验证用户名格式
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username.data):
            raise ValidationError('用户名必须以字母开头，只能包含字母、数字和下划线')

    def validate_email(self, email):
        """验证邮箱是否已存在"""
        if UserRepository.email_exists(email.data):
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')

    def validate_password(self, password):
        """验证密码强度"""
        pwd = password.data
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', pwd):
            raise ValidationError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValidationError('密码必须包含至少一个特殊字符 (!@#$%^&*(),.?":{}|<>)')


class LoginForm(FlaskForm):
    """用户登录表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空')
    ])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class TaskForm(FlaskForm):
    """任务表单，用于创建和更新任务"""
    title = StringField('标题', validators=[
        DataRequired(message='任务标题不能为空'),
        Length(min=1, max=100, message='标题长度必须在1-100个字符之间')
    ])
    content = TextAreaField('内容', validators=[
        DataRequired(message='任务内容不能为空'),
        Length(min=1, max=5000, message='内容长度必须在1-5000个字符之间')
    ])
    due_date = StringField('截止日期', validators=[Optional()], render_kw={'type': 'datetime-local'})
    submit = SubmitField('保存')

    def validate_due_date(self, due_date):
        """验证截止日期是否有效"""
        if due_date.data:
            try:
                parsed_date = datetime.strptime(due_date.data, '%Y-%m-%dT%H:%M')
                if parsed_date < datetime.utcnow():
                    raise ValidationError('截止日期不能早于当前时间')
            except ValueError:
                raise ValidationError('请输入有效的日期时间格式')


class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('当前密码', validators=[
        DataRequired(message='请输入当前密码')
    ])
    new_password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=8, message='密码长度至少为8位')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('new_password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('修改密码')

    def validate_new_password(self, new_password):
        """验证新密码强度"""
        pwd = new_password.data
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', pwd):
            raise ValidationError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValidationError('密码必须包含至少一个特殊字符')


class SearchForm(FlaskForm):
    """搜索表单"""
    keyword = StringField('搜索', validators=[
        DataRequired(message='请输入搜索关键词'),
        Length(min=1, max=100)
    ])
    submit = SubmitField('搜索')
