import json

from flask import request

from __init__ import create_app
from entity import database
from entity.model import User


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
def add():
    data = request.get_json()
    email = data['eamil']
    name = data['name']
    password = data['password']

    database.add_instance(User, eamil=email, name=name, password=password)
    return json.dumps("Added"), 200