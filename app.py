from flask import Flask

from crypt import methods
from urllib import request
import datetime as dt
from s3bucket.s3_connect import s3
from s3bucket.s3_upload import s3_put_object


app = Flask(__name__)
app.config.update(DEBUG=True)

@app.route('/hello')
def welcome():
    return 'Hello world'


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