from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import Required,Regexp,EqualTo,Length
from wtforms import ValidationError


class LoginFrom(FlaskForm):
    phone=StringField('手机号',validators=[Required(),Length(11,12)])
    password=PasswordField('密码',validators=[Required()])
    submit=SubmitField('登录')
    