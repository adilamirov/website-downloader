FROM python:3.7-alpine

RUN apk update && apk add g++ gcc python3-dev libxslt-dev zip

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

