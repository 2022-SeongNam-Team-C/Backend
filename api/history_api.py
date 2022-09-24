from flask import request, Blueprint
import json
from entity.model import Image
from flask_restx import Resource, Namespace
import jwt as pyjwt

History = Namespace('api/v1')
bp = Blueprint('history', __name__, url_prefix='/api/v1')
secrets_key = 'Ladder_teamc'
# History : User Id에 대한 이미지 URL불러오기
@History.route('/s3/history/<id>')
class history(Resource):
    def get(self):

        header_request = request.headers
        bearer = header_request.get('Authorization')

        if not bearer:
            return {"error": "You don't have access authentication."}, 401
            
        access_token = bearer.split()[1]
        user_id = pyjwt.decode(access_token, secrets_key, 'HS256')['sub']

        images = Image.query.filter_by(user_id=user_id).all()
        all_image = []
        for image in images:
            new_image = {
                "image_url": image.result_url
            }
            all_image.append(new_image)
        

        return json.dumps(all_image), 200
