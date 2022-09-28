import imp
from os import access
from flask import jsonify, request
from flask_jwt_extended import ( JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity)
from config.auth import (deauthenticate_user,
                  refresh_authentication, get_authenticated_user,
                  auth_required, AuthenticationError)
from flask_bcrypt import Bcrypt
import redis
from flask import Response
from __init__ import create_app
from entity import database
from entity.model import User
from entity.model import db
from flask_restx import Api, Resource# Api 구현을 위한 Api 객체 import
from api.email_api import bp as email_module
from api.s3_api import bp as s3_module
from api.history_api import bp as history_module
from datetime import datetime as dt
from api.email_api import Email
from api.s3_api import s3
from api.history_api import History
from crypt import methods
from flask_cors import CORS
import jwt as pyjwt
from prometheus_client import generate_latest, REGISTRY, Counter, Gauge, Histogram


# flask App
app = create_app()
CORS(app)
app.config.update(DEBUG=True)
app.register_blueprint(email_module, url_prefix = '/api/v1')
app.register_blueprint(s3_module, url_prefix = '/api/v1')
app.register_blueprint(history_module, url_prefix = '/api/v1')

# Swagger
api = Api(app, version=1.0, title="ladder api", description='ladder api docs', doc='/api-docs')  # Flask 객체에 Api 객체 등록
ladder_api = api.namespace('api/v1', description='ladder api docs')
api.add_namespace(Email, '')
# api.add_namespace(s3, '')
api.add_namespace(History, '')

# login token
secrets_key = 'Ladder_teamc'
app.config['JWT_SECRET_KEY'] = secrets_key  # JWT 시크릿 키
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60 * 60
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 60 * 60 * 24 * 14
app.config['JWT_TOKEN_LOCATION'] = ['json']   # jwt 토큰을 점검할 때 확인할 위치
jwt = JWTManager(app)
jwt_redis = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
bcrypt = Bcrypt(app)


# prometheus
REQUESTS = Counter('http_requests_total', 'Total HTTP Requests (count)', ['method', 'endpoint', 'status_code'])
IN_PROGRESS = Gauge('http_requests_inprogress', 'Number of in progress HTTP requests')
TIMINGS = Histogram('http_request_duration_seconds', 'HTTP request latency (seconds)')


@ladder_api.route('/auth/signin')    # login api
class Signin(Resource):
    @TIMINGS.time()
    @IN_PROGRESS.track_inprogress()
    def post(self):
        if not request.is_json:
            return {"error": "Missing JSON data in request."}, 400

        email = request.json.get('email')
        password = request.json.get('password')
        
        if not email:
            REQUESTS.labels(method='POST', endpoint="/auth/signin", status_code=400).inc()  
            return {"error": "Missing email parameter."}, 400
        if not password:
            REQUESTS.labels(method='POST', endpoint="/auth/signin", status_code=400).inc()  
            return {"error": "Missing password parameter."}, 400
    
        user = User.query.filter_by(email=email).all()
        
        if len(user) == 0:
            REQUESTS.labels(method='POST', endpoint="/auth/signin", status_code=404).inc()  
            return {"error": "We can't find this user."}, 404

        if not User.check_password(user[0], password):
            REQUESTS.labels(method='POST', endpoint="/auth/signin", status_code=403).inc()  
            return {"error": "Please check your email and password."}, 403

        user_refresh_key = email + '_refresh'
        user_access_key = email + '_access'

        is_access_token = jwt_redis.get(user_access_key)

        if is_access_token:
            jwt_redis.delete(user_access_key)

        user_name = User.query.filter(User.email == email).first().name
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        jwt_redis.set(user_refresh_key, refresh_token, app.config['JWT_REFRESH_TOKEN_EXPIRES'])

        response_dict = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "name": user_name
        }
        REQUESTS.labels(method='POST', endpoint="/auth/signin", status_code=200).inc()  
        return response_dict, 200 

@ladder_api.route('/auth/signout')   # logout api
class Signout(Resource):
    @TIMINGS.time()
    @IN_PROGRESS.track_inprogress()
    def post(self): 
        header_request = request.headers
        bearer = header_request.get('Authorization')

        if not bearer:
            REQUESTS.labels(method='POST', endpoint="/auth/signout", status_code=401).inc() 
            return {"error": "You don't have access authentication."}, 401

        access_token = bearer.split()[1]
        
        # check is expired token
        try:
            user = pyjwt.decode(access_token, app.config['JWT_SECRET_KEY'], 'HS256')['sub']
            user_refresh_key = user + '_refresh'
            user_access_key = user+ '_access'
            jwt_redis.delete(user_refresh_key)
            jwt_redis.set(user_access_key, access_token, 60 * 30)
            response_dict = {
                "msg": "success logout",
                "user": user
            }

            REQUESTS.labels(method='POST', endpoint="/auth/signout", status_code=200).inc() 
            return response_dict, 200
        except pyjwt.ExpiredSignatureError:
            REQUESTS.labels(method='POST', endpoint="/auth/signout", status_code=401).inc() 
            return {"error": "This Token is expired."}, 401


@ladder_api.route('/auth/signup')   # register users api
class Signup(Resource):
    @TIMINGS.time()
    @IN_PROGRESS.track_inprogress()
    def post(self):  
        if not request.is_json:
            REQUESTS.labels(method='POST', endpoint="/auth/signup", status_code=400).inc()
            return {"error": "Missing JSON in request."}, 400

        email = request.json.get('email')
        password = request.json.get('password')
        name = request.json.get('name')

        if not email:
            REQUESTS.labels(method='POST', endpoint="/auth/signup", status_code=400).inc()
            return {"error": "Missing email parameter."}, 400
        if not password:
            REQUESTS.labels(method='POST', endpoint="/auth/signup", status_code=400).inc()
            return {"error": "Missing password parameter."}, 400
        if not name:
            REQUESTS.labels(method='POST', endpoint="/auth/signup", status_code=400).inc()
            return {"error": "Missing name parameter."}, 400

        # 이메일 중복검사
        user = User.query.filter_by(email=email).all()
        if len(user) != 0:
            REQUESTS.labels(method='POST', endpoint="/auth/signup", status_code=409).inc()
            return {"error": "This email is already registered."}, 409
            # 409 conflict error, 리소스 충돌을 의미하는 상태코드 전송
            # 리소스의 현재 상태와 충돌해서 해당 요청을 처리할 수 없어 클라이언트가 충돌을 수정해서 다시 요청을 보내야할 때 사용
        database.add_instance(User, name=name, email=email, password=password)

        user_dict = {
            "user_id": User.query.filter(User.email == email).first().user_id,
            "email": User.query.filter(User.email == email).first().email,
            "password": User.query.filter(User.email == email).first().password,
            "name": User.query.filter(User.email == email).first().name
        }

        REQUESTS.labels(method='POST', endpoint="/auth/signup", status_code=200).inc()
        return user_dict, 200

@ladder_api.route('/auth/refresh')  # refresh access token api
class Resignin(Resource):
    @TIMINGS.time()
    @IN_PROGRESS.track_inprogress()
    def get(self):
        header_request = request.headers
        bearer = header_request.get('Authorization')

        if not bearer:
            REQUESTS.labels(method='GET', endpoint="/auth/refresh", status_code=401).inc()  
            return {"error": "You don't have access authentication."}, 401

        refresh_token = bearer.split()[1]
        
        user = pyjwt.decode(refresh_token, app.config['JWT_SECRET_KEY'], 'HS256')['sub']
        user_refresh_key = user + '_refresh'

        is_refresh = jwt_redis.get(user_refresh_key)
        if not is_refresh:
            REQUESTS.labels(method='GET', endpoint="/auth/refresh", status_code=401).inc()  
            return {"msg": "This is a invalid user."}, 401

        if refresh_token != is_refresh:
            REQUESTS.labels(method='GET', endpoint="/auth/refresh", status_code=500).inc()  
            return {"msg": "server error"}, 500

        access_token = create_access_token(identity=user)
        response_dict = {
            "access_token": access_token
        }
        REQUESTS.labels(method='GET', endpoint="/auth/refresh", status_code=200).inc()  
        return response_dict, 200

@app.route('/metrics')
@IN_PROGRESS.track_inprogress()
@TIMINGS.time()
def metrics():
    REQUESTS.labels(method='GET', endpoint="/metrics", status_code=200).inc()
    return generate_latest(REGISTRY)
    

if __name__ == '__main__':
    app.run(debug=True, port=5123)