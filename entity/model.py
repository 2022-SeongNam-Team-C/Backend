import flask_sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = flask_sqlalchemy.SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    create_at = db.Column(db.TIMESTAMP, server_default = db.func.now() )
    update_at = db.Column(db.TIMESTAMP, server_default = db.func.now(), onupdate=datetime.now )

    def __init__(self, name, email, password, **kwargs):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    image_url = db.Column(db.String(150))
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now )

#    create_at = db.Column(db.TIMESTAMP, server_default = db.func.now() )
#    update_at = db.Column(db.TIMESTAMP, server_default = db.func.now(), onupdate=datetime.now )