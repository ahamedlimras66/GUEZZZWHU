
from flask_wtf import FlaskForm
from wtforms.fields.html5 import TelField, EmailField
from wtforms import StringField, PasswordField, IntegerField, DateField
from wtforms.validators import InputRequired, Length, Required, EqualTo


class SigupForm(FlaskForm):
    username = StringField("",validators=[InputRequired(), Length(max=15, min=4)])
    password = PasswordField("password", validators=[InputRequired(), Length(max=80, min=8), EqualTo('re_password',message="Passwords must match")])
    re_password = PasswordField("re_password")
    phone_no = TelField("phoneno")
    email = EmailField('email', validators=[InputRequired()])
    dob = DateField('Date', format="%m/%d/%Y")