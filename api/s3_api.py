from flask import request, Blueprint
from werkzeug.utils import secure_filename

from crypt import methods
from datetime import datetime as dt

from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_object

bp = Blueprint('s3', __name__, url_prefix='/api/v1')
# bp.config.update(DEBUG=True)

@bp.route('/s3/image-upload', methods=['POST'])
def s3upload_test():
    # html에서 가져온 이미지 
    file = request.files['file']
    file.save(secure_filename(file.filename))

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    image_type = file.filename.split('.')[-1]
    image_name = dt.now().strftime(f"{filename}--%Y-%m-%d-%H-%M-%S.{image_type}")
    
    # s3버킷에 업로드
    s3_put_object(s3, 'ladder-s3-bucket', file, image_name)

    # 현재 로그인 사용자 정보
    user_id = 1

    # postgres image table에 업로드
    image_url = "s3://ladder-s3-bucket/images/"+image_name
    image_url = image_url.replace(" ","/")
    database.add_instance(Image, user_id = user_id, image_url = image_url)

    return "성공적으로 사진이 S3에 저장되었습니다."