from flask import current_app, request, Blueprint, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from flask_restx import Resource, Namespace
import jwt as pyjwt
import redis

Email = Namespace('api/v1')
bp = Blueprint("Emailsend", __name__, url_prefix="/api/v1")
secrets_key = 'Ladder_teamc'

jwt_redis = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

@Email.route('/images/transmission')
class Emailsend(Resource):
    def post(self):
        mail = Mail(current_app)
        current_app.config['MAIL_SERVER']='smtp.gmail.com'
        current_app.config['MAIL_PORT']=465
        current_app.config['MAIL_USERNAME']='hee98.09.14@gmail.com'
        current_app.config['MAIL_PASSWORD']='gnsnfprwllcfsocy'
        current_app.config['MAIL_USE_TLS']=False
        current_app.config['MAIL_USE_SSL']=True
        mail = Mail(current_app)

        header_request = request.headers
        bearer = header_request.get('Authorization')
        
        # no login user email send
        if not bearer:
            no_user = request.form['email']
            file = request.files['file']
            file.save(secure_filename(file.filename))
            msg = Message('Ladder_추억의 사다리에서 보낸 편지', sender='hee98.09.14@gmail.com', recipients=[no_user])
            msg.body = '완성된 사진을 보내드립니다. 오늘도 즐거운 하루 되시길 바라요 :)'
            with current_app.open_resource(secure_filename(file.filename)) as fp:
                msg.attach(secure_filename(file.filename), 'image/jpg', fp.read())
            mail.send(msg)
            return {"msg": "Email send success"}, 200
    

        # login user email send
        access_token = bearer.split()[1]
        
        # check is expired token
        try:
            user = pyjwt.decode(access_token, secrets_key, 'HS256')['sub']
            # check signout user
            user_access_key = user + '_access'
            is_logout = jwt_redis.get(user_access_key)
            if is_logout:
                return {"msg": "This is a invalid user."}, 401

            file = request.files['file']
            file.save(secure_filename(file.filename))
            msg = Message('Ladder_추억의 사다리에서 보낸 편지', sender='hee98.09.14@gmail.com', recipients=[user])
            msg.body = '완성된 사진을 보내드립니다. 오늘도 즐거운 하루 되시길 바라요 :)'
            with current_app.open_resource(secure_filename(file.filename)) as fp:
                msg.attach(secure_filename(file.filename), 'image/jpg', fp.read())
            mail.send(msg)
            return {"msg": "Email send success"}, 200

        except pyjwt.ExpiredSignatureError:
            return {"error": "This Token is expired."}, 401    
