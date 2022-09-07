from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token,
    set_access_cookies, set_refresh_cookies
)
from auth import (deauthenticate_user,
                  refresh_authentication, get_authenticated_user,
                  auth_required, AuthenticationError)
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'Team C'

#JWT 만료 시간입니다. 단위는 초 단위입니다!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 30
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800
jwt=JWTManager(app)
app.config.update(DEBUG=True)
bcrypt=Bcrypt(app)

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



if __name__ == "__main__":
    app.run(port=5123, debug=True)
    
    
    
    
    
