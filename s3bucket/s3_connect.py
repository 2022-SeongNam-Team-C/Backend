import boto3

# aws_secret_access_key는 github에 노출되면 안되므로, 개인적으로 공유합니다.
def s3_connection():
    try:
        s3 = boto3.client(
            service_name = "s3",
            region_name="ap-northeast-2",
            aws_access_key_id='AKIAWLCHMQTOIEJTLTDQ',
            aws_secret_access_key = ''
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3

s3 = s3_connection()    