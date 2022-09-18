import os
import redis

user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
database = os.getenv('PG_DB')
port = os.getenv('PG_PORT')


#.env 파일을 잘 못 불러와, 우선 명시적으로 해놨습니다.
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://postgres:2217@postgres:5432/postgres'
jwt_redis = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)


# 로컬 테스트 환경
# DATABASE_CONNECTION_URI = f'postgresql+psycopg2://postgres:2217@localhost:5432/postgres'
# jwt_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)