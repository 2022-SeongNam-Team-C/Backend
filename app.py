from flask import Flask, request, jsonify
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity,
                                create_refresh_token, set_access_cookies, set_refresh_cookies)
from auth import (deauthenticate_user, refresh_authentication, get_authenticated_user, 
                 auth_required, AuthenticationError)
from flask_bcrypt import Bcrypt

from __init__ import create_app
from entity import database
from entity.model import User, Image
from entity.model import db


app = create_app()
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'Team C'

#JWT 만료 시간입니다. 단위는 초 단위입니다.
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 30
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800
jwt=JWTManager(app)
app.config.update(DEBUG=True)
#app.config['BCRYPT_LEVEL'] = 10

bcrypt=Bcrypt(app)

@app.route('/')
def welcome():
    db.create_all()
    return ("db init finish!")
  
  
## Create user
@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data['email']
    name = data['name']
    password = data['password']

    database.add_instance(User, email=email, name=name, password=password)
    
    return json.dumps("Added"), 200


## Read all user
@app.route('/fetch-users', methods=['GET'])
def fetch_users():
    users = database.get_all(User)
    all_user = []
    for user in users:
        new_user = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "password": user.password,
        }
        all_user.append(new_user)

    return json.dumps(all_user), 200
  
  

#로그인 구현입니다.
@app.route('/api/v1/auth/sighin',methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg":"Missing JSON in request"}), 400
        
    email=request.json.get('email')
    password=request.json.get('password')
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password :
        return jsonify({"msg" : "Missing password parameter"}), 400
        
    access_token=create_access_token(identity=email)
    refresh_token=create_refresh_token(identity=email)
    response = jsonify(access_token=access_token, refresh_token=refresh_token)
    
    set_access_cookies(response=response, encoded_access_token=access_token)
    set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)
    
    return response, 200

#로그아웃
@app.route('/api/v1/auth/signout', methods=['POST'])
@jwt_required(locations=['cookies'])
def logout():
    response = deauthenticate_user()
    return response, 200
  

#회원가입
@app.route('/api/v1/auth/signup', methods=['POST'])
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
     
    encrypted_password = bcrypt.generate_password_hash(password=password.encode('utf-8'), rounds=10).decode()
    
    print('email', email)
    print('password', password)
    print('encrypted_password', encrypted_password)

    db_pwd = "$2b$10$oheJjGmtFzuide30FANYh.nodyigWs.5hbAZSswGPYJ6MzUDCMcHy"
    if not bcrypt.check_password_hash(pw_hash=db_pwd, password=password):
        return jsonify(msg="비밀번호를 확인해주세요."), 403

    return jsonify({"msg": "register success"}), 201
  
  
# 토큰 재발행하는 코드
@app.route('/api/v1/auth/refresh', methods=['GET'])
@jwt_required(refresh=True, locations=['cookies'])
def refreshAuth():
    token = request.cookies.get('refresh_token_cookie')
    response = refresh_authentication(token)
    return response, 200


if __name__ == "__main__":
    app.run(port=5123, debug=True)
    
    
    
    
    
