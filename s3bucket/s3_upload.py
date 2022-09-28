from .s3_connect import s3

def s3_put_result_image(s3, bucket, file, filename) :
    try: 
        s3.put_object(
            Body = file,
            Bucket = bucket,
            Key = f'result/{filename}',
            ContentType = file.content_type,
            ACL = "public-read"
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
            ContentType = file.content_type,
            ACL = "public-read"
        )
    except Exception as e:
        return False
    return True