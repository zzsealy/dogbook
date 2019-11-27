from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class ResetForm(FlaskForm):
    email = StringField('请输入邮箱:', validators=[DataRequired()])
    submit = SubmitField('发送')



class RegistrationForm(FlaskForm):
    email = StringField('邮箱（找回密码会用到）', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    nickname = StringField('起个昵称', validators=[DataRequired(), Length(6, 128)])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已经被注册！')

    def validate_nikename(self, field):
        if User.query.filter_by(nikename=field.data).first():
            raise ValidationError('用户名已经被使用！')
