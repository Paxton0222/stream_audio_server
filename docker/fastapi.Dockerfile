FROM python:3.10.9-alpine3.17

ARG env_mode

WORKDIR /app

COPY ./ /app
COPY .env.${env_mode} .env

RUN apk update \
    && apk add pkgconfig \
    && apk add --no-cache --virtual build-deps gcc python3-dev musl-dev libc-dev libffi-dev mariadb-dev \
    && pip install --no-cache-dir -r requirements.txt
RUN rm /var/cache/apk/*

EXPOSE 8000

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
