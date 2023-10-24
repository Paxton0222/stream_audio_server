#!/bin/sh
watchmedo auto-restart --directory=./ --patterns="*.py" --recursive -- uvicorn app.server:app --log-level=info --host="0.0.0.0"
# gunicorn app.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --reload