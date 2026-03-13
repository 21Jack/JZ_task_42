from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime
import re


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=8, message='密码长度至少8位')
    ])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        from todoapp.models.user import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')

    def validate_email(self, email):
        from todoapp.models.user import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱。')
    
    def validate_password(self, password):
        pwd = password.data
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('密码需包含至少一个大写字母')
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('密码需包含至少一个小写字母')
        if not re.search(r'\d', pwd):
            raise ValidationError('密码需包含至少一个数字')


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class TaskForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('内容', validators=[DataRequired()])
    due_date = StringField('截止日期', validators=[], render_kw={'type': 'datetime-local'})
    priority = SelectField('优先级', choices=[
        ('low', '低'),
        ('medium', '中'),
        ('high', '高')
    ], default='medium')
    submit = SubmitField('保存')

    def validate_due_date(self, due_date):
        if due_date.data:
            try:
                parsed_date = datetime.strptime(due_date.data, '%Y-%m-%dT%H:%M')
                if parsed_date < datetime.utcnow():
                    raise ValidationError('截止日期不能早于当前时间。')
            except ValueError:
                raise ValidationError('请输入有效的日期时间格式 (YYYY-MM-DD HH:MM)。')
