from celery import Celery
from flask import jsonify

from s3bucket import s3_connect
from api import s3_api
from entity.model import Image
from entity import database

from datetime import datetime as dt
from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_result_image, s3_put_origin_image
from config.ai_config import RBMQ_CONNECTION_URI


app = Celery('tasks',
             broker=RBMQ_CONNECTION_URI)


# 사진 받아오는 함수 
def saveOriginImage(file, email) :

    # 이메일 받아오면 user_id 찾기
    sql = f"SELECT user_id \
        FROM user \
        WHERE email='{email}'"
    cursor = database.session_execute(sql)
    user_id = cursor.fetchall()[0][0]

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    image_type = file.filename.split('.')[-1]
    image_created = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
    image_name = f"{image_created}--{filename}.{image_type}"

    # s3버킷에 업로드
    s3_put_result_image(s3, 'ladder-s3-bucket', file, image_name)
    
    # postgres image table에 origin_url 업로드
    origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+image_name
    origin_url = origin_url.replace(" ","/")
    database.add_instance(Image, user_id = user_id, origin_url = origin_url, is_deleted = False)

    print("성공적으로 사진이 S3에 저장되었습니다.")


    # celery가 처리할 거
        # api요청 (ai 서버)


    # upload s3 .. (이건 만들어진 api로 보내도 됨 아니면 그냥 여기에 함수 쓰기)