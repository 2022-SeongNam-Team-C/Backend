from flask import request, Blueprint
from werkzeug.utils import secure_filename

from entity import database
from entity.model import Image

from crypt import methods
from datetime import datetime as dt

from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_result_image, s3_put_origin_image


bp = Blueprint('s3', __name__, url_prefix='/api/v1')
# bp.config.update(DEBUG=True)


# s3버킷에 이미지 업로드하며, DB에 image_url과 현재 로그인된 사용자 id저장
# (미완) 현재 로그인된 사용자 정보 
@bp.route('/s3/result/upload-image-url', methods=['POST'])
def upload_image():
    # html에서 가져온 이미지 
    file = request.files['file']

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    image_type = file.filename.split('.')[-1]
    image_created = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
    image_name = f"{image_created}--{filename}.{image_type}"

    # s3버킷에 업로드
    s3_put_result_image(s3, 'ladder-s3-bucket', file, image_name)

    # 현재 로그인 사용자 정보
    user_id = 1
    #writer = get_user()

    # postgres image table에 업로드
    image_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/"+image_name
    image_url = image_url.replace(" ","/")
    database.add_instance(Image, user_id = user_id, image_url = image_url, is_deleted = False)

    return "성공적으로 사진이 S3에 저장되었습니다."


# 변환 이미지 URL불러오기
@bp.route('/s3/result/get-image-url', methods=['POST'])
def get_image():

    data = request.get_json()
    image_name = data['image_name']
    

    result_image_url = f"https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/{image_name}"

    return result_image_url



