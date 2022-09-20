from flask import request, Blueprint
import json

from entity.model import Image
from flask_restx import Resource, Namespace

History = Namespace('api/v1')
bp = Blueprint('history', __name__, url_prefix='/api/v1')

# History : User Id에 대한 이미지 URL불러오기
@History.route('/s3/history/<id>')
class history(Resource):
    def get(self):

        user_id = id

        images = Image.query.filter_by(user_id=user_id).all()
        all_image = []
        for image in images:
            new_image = {
                "image_url": image.result_url
            }
            all_image.append(new_image)
        

        return json.dumps(all_image), 200