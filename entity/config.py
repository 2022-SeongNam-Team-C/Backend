import os
import redis

user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
database = os.getenv('PG_DB')
port = os.getenv('PG_PORT')


DATABASE_CONNECTION_URI = f'postgresql+psycopg2://darling:0829@ladderdb:5432/ladderdb'
jwt_redis = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)


# 로컬 테스트 환경
# DATABASE_CONNECTION_URI = f'postgresql+psycopg2://postgres:2217@localhost:5432/postgres'
# jwt_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
