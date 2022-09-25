from flask import request, Blueprint
import json
from entity.model import Image
from flask_restx import Resource, Namespace
import jwt as pyjwt
import redis

History = Namespace('api/v1')
bp = Blueprint('history', __name__, url_prefix='/api/v1')
secrets_key = 'Ladder_teamc'
jwt_redis = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

# History : User Id에 대한 이미지 URL불러오기
@History.route('/s3/history')
class history(Resource):
    def get(self):

        header_request = request.headers
        bearer = header_request.get('Authorization')

        if not bearer:
            return {"error": "You don't have access authentication."}, 401
            
        access_token = bearer.split()[1]
        user_id = pyjwt.decode(access_token, secrets_key, 'HS256')['sub']

        # check signout user
        user_access_key = user_id+ '_access'
        is_logout = jwt_redis.get(user_access_key)
        if is_logout:
            return {"msg": "This is a invalid user."}, 401

        images = Image.query.filter_by(user_id=user_id).all()
        all_image = []
        for image in images:
            new_image = {
                "image_url": image.result_url
            }
            all_image.append(new_image)
        

        return json.dumps(all_image), 200
