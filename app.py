import json
from flask import Flask, request

from __init__ import create_app
from entity import database
from entity.model import User, Image
from entity.model import db

from api.email_api import bp as email_module
from api.s3_api import bp as s3_module
from api.history_api import bp as history_module


from crypt import methods
from crypt import methods
from urllib import request


from crypt import methods
from urllib import request
import datetime as dt
from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_object


app = Flask(__name__)
app.config.update(DEBUG=True)

app = create_app()
app.register_blueprint(email_module)
app.register_blueprint(s3_module)
app.register_blueprint(history_module)


@app.route('/')
def welcome():
    db.create_all()
    return ("db init finish!")


## Create user
@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data['email']
    name = data['name']
    password = data['password']

    database.add_instance(User, email=email, name=name, password=password)
    
    return json.dumps("Added"), 200


## Read all user
@app.route('/fetch-users', methods=['GET'])
def fetch_users():
    users = database.get_all(User)
    all_user = []
    for user in users:
        new_user = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "password": user.password,
        }
        all_user.append(new_user)

    return json.dumps(all_user), 200


## Uploade image 
@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    user_id = data['user_id']
    image_url = data['image_url']

    database.add_instance(Image, user_id = user_id, image_url = image_url)
    
    return json.dumps("Image Added"), 200


## Read all image
@app.route('/fetch-images', methods=['GET'])
def fetch_images():
    images = database.get_all(Image)
    all_image = []
    for image in images:
        new_image = {
            "image_id": image.image_id,
            "user_id": image.user_id,
            "image_url": image.image_url
        }
        all_image.append(new_image)

    return json.dumps(all_image), 200



@app.route('/s3-image-upload-test', methods=['POST'])
def s3upload_test():
    # html에서 가져온 이미지 
    file = request.file['file_give']

    # 파일 이름 지정
    filename = file.filename.split('.')[0]
    ext = file.filename.split('.')[-1]
    img_name = dt.datetime.now().strtime(f"{filename}--%Y-%m-%d-%H-%M-%S.{ext}")

    # 현재 로그인 사용자 정보
    
    # s3버킷에 업로드
    s3_put_object(s3, 'ladder-s3-bucket', file, img_name)

    # postgres image table에 업로드


if __name__ == "__main__":
    app.run(port=5123, debug=True)
