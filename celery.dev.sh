#!/bin/sh
watchmedo auto-restart --directory=./ --patterns="./app/tasks/*.py" --recursive -- celery -A app worker --concurrency=5 --loglevel=INFO