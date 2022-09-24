import jwt as pyjwt

secrets_key = 'Ladder_teamc'

def check_access_token(header):
    bearer = header.get('Authorization')
    access_token = bearer.split()[1]

    if not access_token:
       no_user = "anonymous"
       response_dict = {
          "user": no_user
       }
       return response_dict, 200

    user = pyjwt.decode(access_token, secrets_key, 'HS256')['sub']
    response_dict = {
          "access_token": access_token,
          "user": user
    }
    return response_dict, 200