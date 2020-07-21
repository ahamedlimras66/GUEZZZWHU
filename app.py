import os, json
from random import randint
from datetime import datetime
from models.form import *
from models.schema import *

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_mail import Mail,Message

from flask_bootstrap import Bootstrap

from flask import Flask, render_template, redirect, jsonify, request, url_for

from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# config file
with open('config.json') as f:
  info = json.load(f)

#
next = ''

# main app
app = Flask(__name__)

# WTF-form bootstrap
Bootstrap(app)

# database config
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# mail server config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = info['email']
app.config['MAIL_PASSWORD'] = info['password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# caching user setup
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'


# Create Database table befor first url request
@app.before_first_request
def create_tables():
    db.create_all()
    if User.query.filter_by(username="root").first() is None:
        adminID = User(username="root",
                    password=generate_password_hash("Root 1234",method='sha256'),
                    email=info['email'],
                    dob=datetime.now(),
                    verification=1,
                    otp=111)
        db.session.add(adminID)
        db.session.commit()

# caching current user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class MyAdminIndexView(AdminIndexView):
	def is_accessible(self):
		if current_user.is_authenticated  and (current_user.username=="root"):
			return True
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login', next=request.url))

class MyModelView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated  and (current_user.username=="root"):
			return True
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login', next=request.url))

class UserAdmin(ModelView):
    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password,method='sha256')

class LinkView(MyModelView):
    column_list = ('id', 'user.username')

class LinkCommandView(MyModelView):
    column_list = ('id','link.user.username', 'user.username', 'date_time', 'command')

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserAdmin(User, db.session))
admin.add_view(LinkView(Link, db.session))
admin.add_view(LinkCommandView(LinkCommand, db.session))

# home page
@app.route("/")
def home():
    return render_template("home.html")

# otp gender and send mail
@app.route("/otp_verification")
def otp_verification():
    current_user.otp = ''.join(["{}".format(randint(0, 9)) for num in range(0, 4)]) # generat otp and store in database
    db.session.commit()

    # send a OTP as mail
    msg = Message('OTP verification', sender="GUEZZWHU", recipients=[current_user.email])
    msg.html = render_template("otpgen.html",otp=current_user.otp)
    mail.send(msg)

    return render_template("otp.html", error=None)

# check OTP
@app.route("/verify", methods=['POST','GET'])
def verify():
    # reading otp
    otp = request.form['ccodeBox1'] + request.form['ccodeBox2'] + request.form['ccodeBox3'] + request.form['ccodeBox4']

    # Checking otp
    if current_user.otp == otp:
        # make accout verified
        current_user.verification = 1
        db.session.commit()

        return redirect("/profile")
    else:
        error = "worng otp"
        return render_template("otp.html", error=error)

# Login check
@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    form = LoginForm()
    global next
    if request.args.get('next'):
        next = request.args.get('next')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
                if current_user.verification == 1:
                    if next:
                        return redirect(next)
                    else:
                        return redirect("/profile")
                else:
                    return redirect("/otp_verification")
            else:
                error = "Invalid password"
        else:
            error = "username not exist"
    return render_template("login.html", form=form, error=error)

# Creat new accout
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
                            otp=''.join(["{}".format(randint(0, 9)) for num in range(0, 4)]),
                            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect("/otp_verification")
        else:
            error = "username exist"
    return render_template("sigup.html", form=form, error=error)

# Profile
@app.route("/profile")
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    link = Link.query.filter_by(user_id=current_user.id).first()
    cmd = None
    if link:
        cmd = LinkCommand.query.filter_by(link_id=link.id)
    return render_template("profile.html", user=user, link=link, cmd=cmd)

# create user command link
@app.route("/create_link/<user_id>")
@login_required
def create_link(user_id):
    link = Link(user_id=user_id)
    db.session.add(link)
    db.session.commit()

    iteam = {}
    iteam['id'] = link.id
    return jsonify(iteam)

# get user command
@app.route("/link/<int:link_id>/")
@login_required
def link(link_id):
    global next
    next = None
    link = Link.query.filter_by(id=link_id).first()
    if link:
        user = User.query.filter_by(id=link.user_id).first()
        return render_template("commend.html", user=user, link=link)

    else:
        return "invalid link"

@app.route("/save_message", methods=['POST', 'GET'])
@login_required
def save_message():
    message = request.form["cmd"]
    time = datetime.now()

    cmd = LinkCommand(link_id=request.form["id"],
                      commander_id=current_user.id,
                      date_time=time,
                      command=message)
    db.session.add(cmd)
    db.session.commit()
    return redirect("/profile")

#logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# # does nothing
# @app.route("/elements")
# def elements():
#     return render_template("elements.html")

# @app.route("/imgtry")
# def imgtry():
#     return render_template("imgtry.html")

# @app.route("/index")
# def index():
#     return render_template("index.html")



# @app.route("/sample")
# def sample():
#     return render_template("sample.html")


if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(debug=True)