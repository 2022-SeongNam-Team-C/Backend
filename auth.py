from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import abort, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity, decode_token, verify_jwt_in_request, 
                                unset_access_cookies, unset_refresh_cookies, set_access_cookies, set_refresh_cookies, get_jwt)
from jwt import InvalidTokenError

from entity.model import User
import db

class AuthenticationError(Exception):
    """Base Authentication Exception"""
    def __init__(self, msg=None):
        self.msg = msg
    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.msg) + ')'

class InvalidCredentials(AuthenticationError):
    """Invalid username/password"""

class AccountInactive(AuthenticationError):
    """Account is disabled"""

class AccessDenied(AuthenticationError):
    """Access is denied"""

class UserNotFound(AuthenticationError):
    """User identity not found"""    
    
def check_token(access_token):
    try:
        payload = decode_token(access_token)
        if payload['exp'] < datetime.utcnow():  
            payload = None
    except InvalidTokenError:
        payload = None

    return payload

#데이터베이스에서 유저 정보를 가져오는 코드입니다

def get_authenticated_user():
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).all()
    if len(user) == 1:
        return user[0]
    else: 
        raise UserNotFound(identity)

#로그아웃해주는 코드입니다
def deauthenticate_user():
   
    identity = get_jwt_identity()
    response = jsonify({"msg": "logout successful"})
    unset_access_cookies(response)
    unset_refresh_cookies(response)
    return response
    
# 토큰 재발행해주는 코드입니다
def refresh_authentication(request_refresh_token):
     
    user = get_authenticated_user() 

    access_token = create_access_token(identity=user['email'])

    response = jsonify(access_token=access_token, refresh_token=request_refresh_token)
    set_access_cookies(response=response, encoded_access_token=access_token)
    
    exp_timestamp = get_jwt()['exp']
    now = datetime.now(timezone.utc)
    target_timestamp = datetime.timestamp(now + timedelta(hours=10))
    if target_timestamp > exp_timestamp:        
        refresh_token = create_refresh_token(identity=user['email'])
        response = jsonify(access_token=access_token, refresh_token=refresh_token) 
        print(response) 
        set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)

    return response
    
#토큰이 올바른 디비에 있는지 확인하는 코드입니다.
def auth_required(func):
   
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request(locations=['cookies'])
        try:
            user = get_authenticated_user()
            
            print("user", user)
            return func(*args, **kwargs)
        except (UserNotFound, AccountInactive) as error:
            print('authorization failed: %s', error)
            abort(403)
    return wrapper
    
    
    
    
    
    
