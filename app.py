import os
import json
from models.form import *
from models.schema import *
from random import randint
from flask_mail import Mail,Message
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


with open('config.json') as f:
  info = json.load(f)

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = info['email']
app.config['MAIL_PASSWORD'] = info['password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
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

@app.route("/otp_verification")
def otp_verification():
    print(current_user.email)
    current_user.opt=''.join(["{}".format(randint(0, 9)) for num in range(0, 4)])
    db.session.commit()
    msg = Message('OTP verification', sender="GUEZZWHU", recipients=[current_user.email])
    msg.html = render_template("otpgen.html",opt=current_user.opt)
    mail.send(msg)
    return render_template("otp.html", error=None)

@app.route("/verify", methods=['POST','GET'])
def verify():
    opt = request.form['ccodeBox1']+request.form['ccodeBox2']+request.form['ccodeBox3']+request.form['ccodeBox4']
    if current_user.opt == opt:
        current_user.verification = 1
        db.session.commit()
        return redirect("/profile")
    else:
        error = "worng opt"
        return render_template("otp.html", error=error)

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
                if current_user.verification == 1:
                    return redirect('/profile')
                else:
                    return redirect("/otp_verification")
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
                            dob=form.dob.data,
                            verification=0,
                            opt=''.join(["{}".format(randint(0, 9)) for num in range(0, 4)]),
                            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect("/otp_verification")
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

@app.route("/create_link/<user_id>")
@login_required
def create_link(user_id):
    link = Link(user_id=user_id)
    db.session.add(link)
    db.session.commit()

    iteam = {}
    iteam['id'] = link.id
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