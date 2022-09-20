import json
from flask import Flask, request

from __init__ import create_app
from entity import database
from entity.model import User, Image
from entity.model import db
from flask_restx import Api, Resource# Api 구현을 위한 Api 객체 import
from api.email_api import bp as email_module
from api.s3_api import bp as s3_module
from api.history_api import bp as history_module
from api.email_api import Email
from api.s3_api import s3
from api.history_api import History
from crypt import methods
from datetime import datetime as dt

app = Flask(__name__)
app.config.update(DEBUG=True)
app = create_app()

app.register_blueprint(email_module, url_prefix = '/api/v1')
app.register_blueprint(s3_module, url_prefix = '/api/v1')
app.register_blueprint(history_module, url_prefix = '/api/v1')

@app.route('/')
def welcome():
    db.create_all()
    return ("db init finish!")

api = Api(app, version=1.0, title="ladder api", description='ladder api docs', doc='/api-docs')  # Flask 객체에 Api 객체 등록
ladder_api = api.namespace('api/v1', description='ladder api docs')

api.add_namespace(Email, '')
api.add_namespace(s3, '')
api.add_namespace(History, '')

## Create user
@ladder_api.route('/create-user')
class Createuser(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        name = data['name']
        password = data['password']

        database.add_instance(User, email=email, name=name, password=password)
        
        return json.dumps("Added"), 200

## Read all user 
@ladder_api.route('/fetch-users')
class Fetchusers(Resource):
    def get(self):
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
@ladder_api.route('/upload-image')
class Uploadimage(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        image_url = data['image_url']

        database.add_instance(Image, user_id = user_id, image_url = image_url)
        
        return json.dumps("Image Added"), 200


## Read all image
@ladder_api.route('/fetch-images')
class Fetchimage(Resource):
    def get(self):
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)