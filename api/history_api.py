from flask import request, Blueprint
from crypt import methods
import json

from entity import database
from entity import model
from entity.model import Image

from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_result_image, s3_put_origin_image


bp = Blueprint('s3', __name__, url_prefix='/api/v1')


# History : User Id에 대한 이미지 URL불러오기
@bp.route('/s3/history/<id>', methods=['GET'])
def history(id):

    user_id = id

    images = Image.query.filter_by(user_id=user_id).all()
    all_image = []
    for image in images:
        new_image = {
            "image_url": image.image_url
        }
        all_image.append(new_image)
    

    return json.dumps(all_image), 200