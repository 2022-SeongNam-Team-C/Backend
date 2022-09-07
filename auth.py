from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import abort, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity, decode_token, verify_jwt_in_request, 
                                unset_access_cookies, unset_refresh_cookies, set_access_cookies, set_refresh_cookies, get_jwt)
from jwt import InvalidTokenError

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




#로그아웃 구현
def deauthenticate_user():
   
    identity = get_jwt_identity()
    response = jsonify({"msg": "logout successful"})
    unset_access_cookies(response)
    unset_refresh_cookies(response)
    return response
    
    
    
    
    
    
    
    
    
    
