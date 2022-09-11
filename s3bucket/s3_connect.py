import boto3

# aws_secret_access_key는 github에 노출되면 안되므로, 개인적으로 공유합니다.
def s3_connection():
    try:
        s3 = boto3.client(
            service_name = "s3",
            region_name = "ap-northeast-2",
<<<<<<< HEAD
            aws_access_key_id = "AKIAWLCHMQTOIEJTLTDQ",
            aws_secret_access_key = ""
=======
            aws_access_key_id = "AKIAWLCHMQTOCDKV5F67",
<<<<<<< HEAD
            aws_secret_access_key = "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"
>>>>>>> aa23cd2 (Fix : #8 aws 업로드 오류 해결 및 create_at 오류 해결 진행)
=======
            aws_secret_access_key = ""
>>>>>>> b7d667f (Chore : #8 Delete aws_secret_access_key)
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3

s3 = s3_connection()    