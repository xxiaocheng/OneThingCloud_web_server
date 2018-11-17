from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required,Length
from wtforms import ValidationError


class CreateTaskForm(FlaskForm):
    url=StringField('下载链接:',validators=[Required()])
    subit=SubmitField('添加任务 ')