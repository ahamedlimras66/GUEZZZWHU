import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from models.schema import *
from models.form import *

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sigup", methods=['POST', 'GET'])
def sigup():

    form = SigupForm()
    print(form.password.data, form.re_password.data, form.dob.data, form.email.data, form.username.data)
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print(form.password.data, form.re_password.data)

    return render_template("sigup.html", form=form)






@app.route("/elements")
def elements():
    return render_template("elements.html")

@app.route("/imgtry")
def imgtry():
    return render_template("imgtry.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/sample")
def sample():
    return render_template("sample.html")


if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(debug=True)