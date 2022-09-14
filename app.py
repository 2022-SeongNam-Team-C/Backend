from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token,
    set_access_cookies, set_refresh_cookies
)
from auth import (deauthenticate_user,
                  refresh_authentication, get_authenticated_user,
                  auth_required, AuthenticationError)
from flask_bcrypt import Bcrypt
import json

from entity import database
from entity.model import User
from init import create_app


app = create_app()


app.config['JWT_SECRET_KEY'] = 'Team C'
# 1800 JWT 만료 시간 설정 부분임 (단위 : 초)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 30
# 604800
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 50
jwt = JWTManager(app)


# app.config['SECRET_KEY'] = 'Team C'
# app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app)



'''
로그인
'''
@app.route('/api/v1/auth/signin', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email')
    password = request.json.get('password')
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # 데이터베이스에서 비밀번호 가져오기
    # 그리고 입력한 비밀번호와 비교
    # if not bcrypt.check_password_hash(password, '12341234').decode('utf-8'):
    #    return jsonify(msg="비밀번호를 확인해주세요."), 403
    user = User.query.filter_by(email=email).all()[0]
    if not User.check_password(user, password):
        return jsonify(msg="비밀번호를 확인해주세요."), 403 


    # 액세스토큰과 리프레시토큰 생성하는 코드
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    response = jsonify(access_token=access_token, refresh_token=refresh_token)

    # set_refresh_token_db(email=email, refresh_token=refresh_token)

    # 토큰 쿠키에 저장
    set_access_cookies(response=response, encoded_access_token=access_token)
    set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)

    return response, 200

#로그아웃
@app.route('/api/v1/auth/signout', methods=['POST'])
@jwt_required(locations=['cookies'])
def logout():
    # 쿠키 삭제 필요함 삭제하는 코드
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

          

    # 회원가입 암호화 코드 ( encrypted_password 를 디비에 저장 )
    # encrypted_password = bcrypt.generate_password_hash(password=password.encode('utf-8'), rounds=10).decode()
    
  

    # 데이터베이스에 저장하는 코드 들어갈 부분
    database.add_instance(User, name=name, email=email, password=password)


    
    #디비에 저장된 비밀번호입니다.
    #db_pwd="$2b$10$oheJjGmtFzuide30FANYh.nodyigWs.5hbAZSswGPYJ6MzUDCMcHy"
    #if not bcrypt.check_password_hash(pw_hash=db_pwd, password=password):
    #    return jsonify(msg="비밀번호를 확인해주세요."),403
        
    return jsonify(msg="success"), 201

# 토큰 재발행
@app.route('/api/v1/auth/refresh', methods=['GET'])
@jwt_required(refresh=True, locations=['cookies'])
def refreshAuth():
    token = request.cookies.get('refresh_token_cookie')
    response = refresh_authentication(token)
    return response, 200

@app.route('/sendEmail', methods=['POST'])
@auth_required
def authTest():
    # 이메일 전송 코드 작성
    return jsonify(msg="success"), 200

if __name__ == '__main__':
    app.run(debug=True, port=5123)

