from flask import request, Flask
from s3bucket.s3_upload import s3_put_origin_image, s3_put_result_image
from module.model_module import make_photo
from api.s3_api import s3
from datetime import datetime

app = Flask(__name__) 

@app.route('/api/v1/images/result', methods=['POST'])
def get_image():
    #file = request.files['file']
    origin_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/origin/20220929-171510--sdsd.jpg"
    # params = request.get_json() ## 이미지 url 받아오기
    print(origin_url)

    return make_photo(origin_url)
    #days = datetime.today()
    #file_name = days.strftime('%Y-%m-%d-%H-%M-%S') + '.jpg'
    #s3_put_result_image(s3, 'ladder-s3-bucket', file, file_name)

    #result_url = "https://ladder-s3-bucket.s3.ap-northeast-2.amazonaws.com/result/"+file_name

    #return result_url

if __name__ == '__main__':
    app.run(debug=True, port=5123)