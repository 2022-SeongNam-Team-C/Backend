from flask import request, Flask
from s3bucket.s3_upload import s3_put_origin_image, s3_put_result_image
from module.model_module import make_photo
from api.s3_api import s3
from datetime import datetime
from s3bucket.s3_connect import s3
from werkzeug.utils import secure_filename

app = Flask(__name__) 

@app.route('/api/v1/images/result', methods=['POST'])
def get_image():
    file = request.files['file']
    s3.put_object(
            Body = file,
            Bucket = 'ladder-s3-bucket',
            Key = f'origin/{secure_filename(file.filename)}',
            ContentType = 'image/jpeg'
    )
    origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/"+secure_filename(file.filename)
    # params = request.get_json() ## 이미지 url 받아오기
    print(origin_url)

    return make_photo(origin_url)

if __name__ == '__main__':
    app.run(debug=True, port=5123)