from .s3_connect import s3

def s3_put_result_object(s3, bucket, file, filename) :
    '''
    s3 bucket에 지정 파일 업로드
    :param s3 : 연결된 s3 객체(boto3 client)
    :param bucket : 버킷명
    :return 성공시 true, 실패시 false
    '''
    try: 
        s3.put_object(
            Body = file,
            Bucket = bucket,
            Key = f'result/{filename}',
            ContentType = file.content_type
        )
    except Exception as e:
        return False
    return True


def s3_put_origin_image(s3, bucket, file, filename) :
    try: 
        s3.put_object(
            Body = file,
            Bucket = bucket,
            Key = f'origin/{filename}',
            ContentType = file.content_type
            Key = f'images/{filename}',
            ContentType = file.content_type,
            ACL='public-read'
        )
    except Exception as e:
        return False
    return True