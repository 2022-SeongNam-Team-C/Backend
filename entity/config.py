import os

user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
database = os.getenv('PG_DB')
port = os.getenv('PG_PORT')


#.env 파일을 잘 못 불러와, 우선 명시적으로 해놨습니다.
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://root:1234@localhost:5123/local'