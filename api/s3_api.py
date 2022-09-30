from flask import request, Blueprint
from werkzeug.utils import secure_filename

from entity import database
from entity.model import Image
from entity.model import User
from crypt import methods
from datetime import datetime as dt

from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_result_image, s3_put_origin_image
from flask_restx import Resource, Namespace
import jwt as pyjwt
import redis

secrets_key = 'Ladder_teamc'
jwt_redis = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
bp = Blueprint('s3', __name__, url_prefix='/api/v1')

# s3 = Namespace('api/v1')

# s3버킷에 이미지 업로드하며, DB에 image_url과 현재 로그인된 사용자 id저장
# (미완) 현재 로그인된 사용자 정보 

@bp.route('/s3/result/upload-image-url', methods=['POST'])
def result_up():
    # html에서 가져온 이미지 
    file = request.files['file']

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    image_type = file.filename.split('.')[-1]
    image_created = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
    image_name = f"{image_created}--{filename}.{image_type}"

    # s3버킷에 업로드
    s3_put_result_image(s3, 'ladder-s3-bucket', file, image_name)

    # 현재 로그인 사용자 정보 (토큰 연결시 수정 예정)
    header_request = request.headers
    bearer = header_request.get('Authorization')

    # upload api for no login users
    if not bearer:
        email = "anonymous@nouser.com"
        id = 10000
        # 이부분은 고민을 좀 해봐야할 것 같음
        # postgres image table에 업로드
        result_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/"+image_name
        result_url = result_url.replace(" ","/")
        database.add_instance(Image, user_id = id, result_url = result_url, is_deleted = False)

        # return "성공적으로 사진이 S3에 저장되었습니다."
        return result_url

    # upload api for login users
    access_token = bearer.split()[1]

    try:
        email = pyjwt.decode(access_token, secrets_key, 'HS256')['sub']

        # check signout user
        user_access_key = email + '_access'
        is_logout = jwt_redis.get(user_access_key)
        if is_logout:
            return {"msg": "This is a invalid user."}, 401

        # writer = get_user()
        id = User.query.filter(User.email == email).first().user_id

        # postgres image table에 업로드
        result_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/"+image_name
        result_url = result_url.replace(" ","/")
        database.add_instance(Image, user_id = id, result_url = result_url, is_deleted = False)

        # return "성공적으로 사진이 S3에 저장되었습니다."
        return result_url
    except pyjwt.ExpiredSignatureError:
        return {"error": "This Token is expired."}, 401

# origin 이미지 S3업로드
# @bp.route('/s3/origin/upload-image-url', methods=['POST'])
def origin_up(file):
    # file = request.files['file']

    filename = file.filename.split('.')[0]
    image_type = file.filename.split('.')[-1]
    image_created = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
    image_name = f"{image_created}--{filename}.{image_type}"

    s3_put_origin_image(s3, 'ladder-s3-bucket', file, image_name)

    # 현재 로그인 사용자 정보 (토큰 연결시 수정 예정)
    header_request = request.headers
    bearer = header_request.get('Authorization')

    # upload api for no login users
    if not bearer:
        email = "anonymous@nouser.com"
        id = 10000
        origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+image_name
        origin_url = origin_url.replace(" ","/")
        database.add_instance(Image, user_id = id, origin_url = origin_url, is_deleted = False)

        # return "성공적으로 사진이 S3에 저장되었습니다."
        return origin_url
    
    # writer = get_user()
    # upload api for login users
    access_token = bearer.split()[1]

    try:
        email = pyjwt.decode(access_token, secrets_key, 'HS256')['sub']

        # check signout user
        user_access_key = email + '_access'
        is_logout = jwt_redis.get(user_access_key)
        if is_logout:
            return {"msg": "This is a invalid user."}, 401

        id =  id = User.query.filter(User.email == email).first().user_id
            
        origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+image_name
        origin_url = origin_url.replace(" ","/")
        database.add_instance(Image, user_id = id, origin_url = origin_url, is_deleted = False)

        # return "성공적으로 사진이 S3에 저장되었습니다."
        return origin_url
    except pyjwt.ExpiredSignatureError:
        return {"error": "This Token is expired."}, 401

# (result)변환 이미지 URL불러오기
@bp.route('/s3/result/get-image-url/<image_name>', methods=['POST'])
def res_result():
    image_name = image_name
    result_image_url = f"https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/{image_name}"

    return result_image_url


# (origin)원본 이미지 URL불러오기
@bp.route('/s3/origin/get-image-url/<image_name>', methods=['POST'])
def res_origin():
    image_name = image_name
    origin_image_url = f"https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/{image_name}"

    return origin_image_url
