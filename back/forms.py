from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class NewDomain(FlaskForm):
    domain = StringField('Домен', validators=[DataRequired()], render_kw={"placeholder": "Добавить домен"})

class NewZone(FlaskForm):
    zone = StringField('Зона', validators=[DataRequired()], render_kw={"placeholder": "Добавить зону"})

class DomainForm(FlaskForm):
    state = BooleanField('Статус')
    domain = StringField('Домен', validators=[DataRequired()])

    def __init__(self, name:str, formdata=None, **kwargs):
        super().__init__(formdata, **kwargs)
        self.domain.render_kw={"value":name}
        self.state.render_kw = {"checked":None}