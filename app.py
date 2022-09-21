from datetime import timedelta
from os import access
from flask import request, jsonify
from __init__ import create_app
from flask_jwt_extended import ( JWTManager, jwt_required, create_access_token, create_refresh_token,)
from auth import (deauthenticate_user,
                  refresh_authentication, get_authenticated_user,
                  auth_required, AuthenticationError)
from flask_bcrypt import Bcrypt
import json
from entity import database
from entity.model import User

app = create_app()
app.config['JWT_SECRET_KEY'] = 'Team C'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 30
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.route('/api/v1/auth/signin', methods=['POST'])    # login api
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email')
    password = request.json.get('password')
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
  
    user = User.query.filter_by(email=email).all()
    # user_email = User.query.filter(User.email == email).first().email
    if len(user) == 0:
        return jsonify(msg="이메일, 비밀번호를 확인해주세요."), 403

    if not User.check_password(user[0], password):
        return jsonify(msg="이메일, 비밀번호를 확인해주세요."), 403 

    user_name = User.query.filter(User.email == email).first().name

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    response = jsonify(access_token=access_token, refresh_token=refresh_token, user_name=user_name)
    return response, 200 

@app.route('/api/v1/auth/signout', methods=['POST'])   # logout api
@jwt_required(locations=['cookies'])
def logout():
    # 쿠키 삭제 필요함 삭제하는 코드
    response = deauthenticate_user()
    return response, 200

@app.route('/api/v1/auth/signup', methods=['POST'])   # register users api
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email')
    password = request.json.get('password')
    name = request.json.get('name')

    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    if not name:
        return jsonify({"msg": "Missing name parameter"}), 400

    # 이메일 중복검사
    user = User.query.filter_by(email=email).all()
    if len(user) != 0:
        return jsonify(msg="이미 가입된 이메일주소입니다."), 403
    database.add_instance(User, name=name, email=email, password=password)

    user_dict = {
        "email": User.query.filter(User.email == email).first().email,
        "password": User.query.filter(User.email == email).first().password,
        "name": User.query.filter(User.email == email).first().name
    }

    user_json = json.dumps(user_dict)
    return user_json

# 토큰 재발행
@app.route('/api/v1/auth/refresh', methods=['GET'])
@jwt_required(refresh=True, locations=['cookies'])
def refreshAuth():
    token = request.cookies.get('refresh_token_cookie')
    response = refresh_authentication(token)
    return response, 200


if __name__ == '__main__':
    app.run(debug=True, port=5123)

