import os
from config.redis_config import RedisClient

user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
database = os.getenv('PG_DB')
port = os.getenv('PG_PORT')


# 길연 : .env 파일을 잘 못 불러와, 우선 명시적으로 해놨습니다.
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://darling:0829@ladderdb:5432/ladderdb'

# redis
redis_users = RedisClient(host='localhost', port=6379, db=0)
redis_clients = RedisClient(host='localhost', port=6379, db=1)
redis_credit_card_information = RedisClient(host='localhost', port=6379, db=2)