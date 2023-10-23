FROM python:3.10.9-alpine3.17

ARG env_mode
ENV ENV_MODE $env_mode

RUN apk update \
    && apk add pkgconfig \
    && apk add --no-cache --virtual build-deps gcc python3-dev musl-dev libc-dev libffi-dev mariadb-dev ffmpeg
RUN rm /var/cache/apk/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env.${ENV_MODE} .env
COPY ./*.${ENV_MODE}.sh /
RUN chmod +x /*.${ENV_MODE}.sh

EXPOSE 8000