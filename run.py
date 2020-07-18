from app import app
from db import db
from models.schema import *
from werkzeug.security import check_password_hash, generate_password_hash


db.init_app(app)

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