import json

from flask import request

from __init__ import create_app
from entity import database
from entity.model import User, Image


app = create_app()

@app.route('/welcome')
def hello():
    return 'This is welcome page'

## fetch user 
@app.route('/fetch-user', methods=['GET'])
def fetch():
    users = database.get_all(User)
    all_user = []
    for user in users:
        new_user = {
            "email": user.email,
            "name": user.name,
            "password": user.password,
        }

        all_user.append(new_user)
    return json.dumps(all_user), 200


## Create User
@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data['email']
    name = data['name']
    password = data['password']

    database.add_instance(User, email=email, name=name, password=password)
    
    return json.dumps("Added"), 200


## Uploade Image 
@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    user_id = data['userid']
    image_url = data['imageurl']
    database.add_instance(Image, user_id = user_id, image_url = image_url)
    
    return json.dumps("Image Added"), 200