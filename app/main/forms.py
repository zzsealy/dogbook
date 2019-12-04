from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email
from wtforms import ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):
    name = StringField('输入你的名字', validators=[DataRequired()])
    submit = SubmitField('提交')

# 普通用户使用的资料修改表单
class EditProfileForm(FlaskForm):
    nickname = StringField('昵称', validators=[Length(3,64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交修改')

# 管理员使用的资料修改表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1,64), Email()])
    nickname = StringField('昵称', validators=[DataRequired(), Length(1,64)])
    role = SelectField('角色', coerce=int)
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # role的choice方法是表单Select必须实现的，选项必须是由一个元组构成的列表，
        # 各元组都包含两个元素：选项的标识符，以及显示在控件的文本。
        # 元组中的标识符是角色ID， 因为这是个整数，所以在role字段中加入 coerce=int参数，把字段值转换为整数。
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self, field):   
        # 首先要检查是否有变化， 只有有变化的情况下，才需要检查是否和其他用户的值重复。 nickname同理。
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册了!', 'warning')
    
    def validate_nickname(self, field):
        if field.data != self.user.nickname and \
            User.query.filter_by(nickname=field.data).first():
            raise ValidationError('昵称已经被占用！', 'warning')


class PostForm(FlaskForm):
    title =  StringField('标题')
    body = PageDownField('内容')
    submit = SubmitField('提交')