import os
from models.form import *
from models.schema import *
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_first_request
def create_tables():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
                return redirect('/profile')
            else:
                error = "Invalid password"
        else:
            error = "username exist"
    return render_template("login.html", form=form, error=error)

@app.route("/sigup", methods=['POST', 'GET'])
def sigup():
    error = None
    form = SigupForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first() == None:
            new_user = User(username=form.username.data,
                            password=generate_password_hash(form.password.data, method='sha256'),
                            gender=dict(form.gender.choices).get(form.gender.data),
                            phone_no=form.phone_no.data,
                            email=form.email.data,
                            dob=form.dob.data
                            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        else:
            error = "username exist"
    return render_template("sigup.html", form=form, error=error)


@app.route("/profile")
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    link = Link.query.filter_by(user_id=current_user.id).first()
    print(link)
    return render_template("profile.html", user=user, link=link)

@app.route("create_link/<user_id>")
@login_required
def create_link(user_id):
    iteam = {}
    iteam['id'] = user_id
    return jsonify(iteam)

@app.route("/link/<link_id>")
@login_required
def link(link_id):
    return link_id


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/elements")
def elements():
    return render_template("elements.html")

@app.route("/imgtry")
def imgtry():
    return render_template("imgtry.html")

@app.route("/index")
def index():
    return render_template("index.html")



@app.route("/sample")
def sample():
    return render_template("sample.html")


if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(debug=True)