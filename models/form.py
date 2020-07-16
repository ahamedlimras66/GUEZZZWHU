
from flask_wtf import FlaskForm
from wtforms.fields.html5 import TelField, EmailField
from wtforms import StringField, PasswordField, IntegerField, DateField, SelectField
from wtforms.validators import InputRequired, Length, Required, EqualTo


class SigupForm(FlaskForm):
    username = StringField("username",validators=[InputRequired(), Length(max=15, min=4)])
    password = PasswordField("password", validators=[InputRequired(), Length(max=80, min=8), EqualTo('re_password',message="Passwords must match")])
    re_password = PasswordField("re_password", validators=[InputRequired(), Length(max=80, min=8)])
    gender = SelectField("gender", validators=[InputRequired()], choices=[(1,'Male'),(2,'Female'),(3,'Other')],coerce=int)
    phone_no = TelField("phoneno", validators=[InputRequired()])
    email = EmailField('email', validators=[InputRequired()])
    dob = DateField('Date', format="%d/%m/%Y", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("username",validators=[InputRequired(), Length(max=15, min=4)])
    password = PasswordField("password", validators=[InputRequired(), Length(max=80, min=8)])

class OTPForm(FlaskForm):
    pass
