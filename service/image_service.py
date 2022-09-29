from celery import Celery
from flask import jsonify,request

from s3bucket import s3_connect
from api import s3_api
from entity import database
from entity.model import User, Image
from entity.model import db

import requests
from datetime import datetime as dt
from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_result_image, s3_put_origin_image
from config.ai_config import RBMQ_CONNECTION_URI, AI_CONVERT_API
import time
import jwt as pyjwt
import redis

import base64
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt


secrets_key = 'Ladder_teamc'
jwt_redis = redis.StrictRedis(host='redis', port=6379, decode_responses=True)



app = Celery('tasks', broker=RBMQ_CONNECTION_URI)



# 사진 받아오는 함수 
def saveOriginImage(file) :
    user_id = 1

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    origin_image_type = file.filename.split('.')[-1]
    origin_image_created = dt.now().strftime('%Y%m%d-%H%M%S')
    origin_image_name = f"{origin_image_created}--{filename}.{origin_image_type}"

    # s3버킷에 업로드
    s3_put_origin_image(s3, 'ladder-s3-bucket', file, origin_image_name)

    # postgres image table에 업로드
    origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+origin_image_name
    origin_url = origin_url.replace(" ","/")
    database.add_instance(Image, user_id = user_id, origin_url = origin_url, is_deleted = False)

    # ai 셀러리 요청, 이제 요 다음부터 비동기처리
    convertImage.delay(origin_url)


@app.task()  
def convertImage(origin_url):

    req = {'img' : origin_url}
    print(req)

    res = requests.post(AI_CONVERT_API,json=req)
    result_json = res.json()
    print("convertImage def : 333333333333")
    # result_url type : <class 'requests.models.Response'>

    # image_dict = {
    #     "converted_image_name": file_name,
    #     "converted_image.png": encoded_string.decode()
    # }

    converted_image_name = result_json['converted_image_name']
    converted_image = result_json['converted_image.png']
    converted_image = converted_image.open(BytesIO(base64.b64decode(base64_string)))

    print("===============app.task finish====================s")
    print("===============app.task finish====================s")
    print("===============app.task finish====================s")
    print(converted_image_name)  
    
    result_url = saveResultImage(converted_image)
    print(result_url)
    print("===============app.task finish====================s")

    return result_url



#  변환된 사진 저장
def saveResultImage(file) :
    print("filename================")
    # AttributeError: 'Response' object has no attribute 'filename'
    # AttributeError: 'bytes' object has no attribute 'filename'
    user_id =1
    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    result_image_type = file.filename.split('.')[-1]
    result_image_created = dt.now().strftime('%Y%m%d-%H%M%S')
    result_image_name = f"{result_image_created}--{filename}.{result_image_type}"

    # s3버킷에 업로드
    s3_put_result_image(s3, 'ladder-s3-bucket', file, result_image_name)
    
    # postgres image table에 origin_url 업로드
    result_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/"+result_image_name
    result_url = result_url.replace(" ","/")

    database.add_instance(Image, user_id = user_id, result_url = result_url, is_deleted = False)

    print("성공적으로 변환된 사진이 S3에 저장되었습니다.")

    return result_url


