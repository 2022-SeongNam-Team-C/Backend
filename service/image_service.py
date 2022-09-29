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

from flask import Flask, jsonify, request
from PIL import Image as pilImage
import json
from io import BytesIO
import base64

secrets_key = 'Ladder_teamc'
jwt_redis = redis.StrictRedis(host='redis', port=6379, decode_responses=True)


app = Celery('tasks', broker=RBMQ_CONNECTION_URI)


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
    database.add_instance(Image, user_id = user_id, origin_url = origin_url)

    # ai 셀러리 요청, 이제 요 다음부터 비동기처리
    convertImage.delay(origin_url)


@app.task()  
def convertImage(origin_url):

    req = {'img' : origin_url}
    print(req)

    json_data = requests.post(AI_CONVERT_API,json=req)
    dict_data = json.loads(json_data)
    img = dict_data['img']
    img = base64.b64decode(img)
    img = BytesIO(img)
    img = pilImage.open(img)
    print("====================sdsdsdsd")
    print(type(img))

    saveResultImage(img)




#  변환된 사진 저장
def saveResultImage(file) :
    print("filename================")

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

    database.add_instance(Image, user_id = user_id, result_url = result_url)

    print("성공적으로 변환된 사진이 S3에 저장되었습니다.")

    return result_url


