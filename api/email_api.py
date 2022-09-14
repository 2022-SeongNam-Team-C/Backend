from flask import current_app, request, Blueprint, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

bp = Blueprint('emailSend', __name__, url_prefix='/api/v1')
# bp.config.update(DEBUG=True)


@bp.route('/images/transmission')
def email_send():
    mail = Mail(current_app)

    current_app.config['MAIL_SERVER']='smtp.gmail.com'
    current_app.config['MAIL_PORT']=465
    current_app.config['MAIL_USERNAME']='hee98.09.14@gmail.com'
    current_app.config['MAIL_PASSWORD']=''
    current_app.config['MAIL_USE_TLS']=False
    current_app.config['MAIL_USE_SSL']=True
    mail = Mail(current_app)

    file = request.files['file']
    file.save(secure_filename(file.filename))
    msg = Message('파일 전송 테스트', sender='hee98.09.14@gmail.com', recipients=['hee98.09.14@gmail.com'])
    msg.body = '메일이 잘 전송되었나요?'
    with current_app.open_resource(secure_filename(file.filename)) as fp:
        msg.attach(secure_filename(file.filename), 'image/png', fp.read())
    
    mail.send(msg)
    return '성공적으로 전송되었습니다.'



    
