import wtforms
from flask_wtf import FlaskForm
from sqlalchemy.sql.functions import current_user
from werkzeug.security import check_password_hash
from wtforms import PasswordField
from wtforms.validators import Email, Length, EqualTo, InputRequired, ValidationError
from models import UserModel, EmailCaptchaModel
from exts import db


# Form：主要就是用来验证前端提交的数据是否符合要求
class RegisterForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])
    captcha = wtforms.StringField(validators=[Length(min=4, max=4, message="验证码格式错误！")])
    username = wtforms.StringField(validators=[Length(min=3, max=20, message="用户名格式错误！")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误！")])
    password_confirm = wtforms.StringField(validators=[EqualTo("password", message="两次密码不一致！")])

    # 自定义验证：
    # 1. 邮箱是否已经被注册
    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message="该邮箱已经被注册！")

    # 2. 验证码是否正确
    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(email=email, captcha=captcha).first()
        if not captcha_model:
            raise wtforms.ValidationError(message="邮箱或验证码错误！")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[InputRequired(message="旧密码不能为空！")])
    new_password = PasswordField('新密码', validators=[
        InputRequired(message="新密码不能为空！"),
        Length(min=6, max=20, message="新密码长度应在6到20个字符之间！")
    ])

    def validate_old_password(self, field):
        """验证旧密码是否正确"""
        if not check_password_hash(current_user.password, field.data):
            raise ValidationError("旧密码错误！")

    def update_password(self, user):
        """更新用户密码"""
        user.set_password(self.new_password.data)
        db.session.commit()

class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误！")])


class QuestionForm(wtforms.Form):
    title = wtforms.StringField(validators=[Length(min=3, max=100, message="标题格式错误！")])
    content = wtforms.StringField(validators=[Length(min=3,message="内容格式错误！")])


class AnswerForm(wtforms.Form):
    content = wtforms.StringField(validators=[Length(min=3, message="内容格式错误！")])
    question_id = wtforms.IntegerField(validators=[InputRequired(message="必须要传入问题id！")])