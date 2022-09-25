from celery import Celery
from flask import jsonify

from s3bucket import s3_connect
from api import s3_api
from entity.model import Image
from entity import database

import requests
from datetime import datetime as dt
from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_result_image, s3_put_origin_image
from config.ai_config import RBMQ_CONNECTION_URI, AI_CONVERT_API


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
    origin_image_type = file.filename.split('.')[-1]
    origin_image_created = dt.now().strftime('%Y%m%d-%H%M%S')
    origin_image_name = f"{origin_image_created}--{filename}.{origin_image_type}"

    # s3버킷에 업로드
    s3_put_origin_image(s3, 'ladder-s3-bucket', file, origin_image_name)
    
    # postgres image table에 origin_url 업로드
    origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+origin_image_name
    origin_url = origin_url.replace(" ","/")
    database.add_instance(Image, user_id = user_id, origin_url = origin_url, is_deleted = False)

    # ai 셀러리 요청, 이제 요 다음부터 비동기처리
    convertImage.delay(origin_url)

    return "성공적으로 사진이 S3에 저장되었습니다."



#  변환된 사진 저장
def saveResultImage(file, email) :

    # 이메일 받아오면 user_id 찾기
    sql = f"SELECT user_id \
        FROM user \
        WHERE email='{email}'"
    cursor = database.session_execute(sql)
    user_id = cursor.fetchall()[0][0]

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    result_image_type = file.filename.split('.')[-1]
    result_image_created = dt.now().strftime('%Y%m%d-%H%M%S')
    result_image_name = f"{result_image_created}--{filename}.{result_image_type}"

    # s3버킷에 업로드
    s3_put_result_image(s3, 'ladder-s3-bucket', file, result_image_name)
    
    # postgres image table에 origin_url 업로드
    result_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+result_image_name
    result_url = result_url.replace(" ","/")
    database.add_instance(Image, user_id = user_id, result_url = result_url, is_deleted = False)

    print("성공적으로 변환된 사진이 S3에 저장되었습니다.")



# celery가 처리할 거
    # api요청 (ai 서버)
@app.task()  
def convertImage(origin_url):
    result_image = requests.post(AI_CONVERT_API, origin_url)
    saveResultImage(result_image.content)