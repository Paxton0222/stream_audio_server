#!/bin/sh

docker-compose up -d && docker-compose down celery-worker && sh server.dev.sh | sh celery.dev.sh | npm run dev