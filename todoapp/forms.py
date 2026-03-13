from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from todoapp.models import User
from datetime import datetime
import re

class RegistrationForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱。')

class LoginForm(FlaskForm):
    """用户登录表单"""
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class TaskForm(FlaskForm):
    """任务表单，用于创建和更新任务"""
    title = StringField('标题', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('内容', validators=[DataRequired()])
    due_date = StringField('截止日期', validators=[], render_kw={'type': 'datetime-local'})
    submit = SubmitField('保存')

    def validate_due_date(self, due_date):
        """验证截止日期是否有效"""
        if due_date.data:
            try:
                # 解析输入的日期时间字符串
                parsed_date = datetime.strptime(due_date.data, '%Y-%m-%dT%H:%M')
                if parsed_date < datetime.utcnow():
                    raise ValidationError('截止日期不能早于当前时间。')
            except ValueError:
                raise ValidationError('请输入有效的日期时间格式 (YYYY-MM-DD HH:MM)。')
