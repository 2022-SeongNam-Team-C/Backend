import flask_sqlalchemy


db = flask_sqlalchemy.SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    create_at = db.Column(db.TIMESTAMP, server_default = db.func.now() )
    upload_at = db.Column(db.TIMESTAMP, server_default = db.func.now() )


class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    image_url = db.Column(db.String(150))
    create_at = db.Column(db.TIMESTAMP, server_default = db.func.now() )
    upload_at = db.Column(db.TIMESTAMP, server_default = db.func.now() )


    # from sqlalchemy_utils import PasswordType
    # hashed_password = db.Column(PasswordType(schemes=["pbkdf2_sha512", "md5_crypt"], deprecated=["md5_crypt"]), )
    # pbkdf2_sha512 는 암호를 해시하는데 사용
    # md5_crypt 는 이후 패스워드를 비교할 때 사용