import os

# AI_SERVER_HOST=os.environ.get('AI_HOST')
# AI_SERVER_PORT=os.environ.get('AI_PORT')

AI_CONVERT_API=f'http://ai:5000/api/v1/images/result'

# RABBITMQ_HOST=os.environ.get('RABBITMQ_HOST')
# RABBITMQ_PORT=os.environ.get('RABBITMQ_PORT')
# RABBITMQ_USER=os.environ.get('RABBITMQ_USER')
# RABBITMQ_PASSWORD=os.environ.get('RABBITMQ_PASSWORD')

RBMQ_CONNECTION_URI=f'amqp://darling:0829@rabbitmq:5672//'