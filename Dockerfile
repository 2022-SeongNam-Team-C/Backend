FROM python:3.9.13

RUN mkdir /backend
WORKDIR /backend

COPY . /backend/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get -y install libpq-dev

RUN POSTGRES_HOST_AUTH_METHOD=trust
