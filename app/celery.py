from celery import Celery
from app.env import env_vars

celery = Celery(
    'music_broadcast',
    broker=f"""pyamqp://{env_vars["RABBITMQ_USER"]}:{env_vars["RABBITMQ_PASS"]}@{env_vars["RABBITMQ_HOST"]}:{env_vars["RABBITMQ_PORT"]}//""",
    backend=f"""redis://{env_vars["REDIS_HOST"]}:{env_vars["REDIS_PORT"]}/0""",
    include=["app.task"]
)

celery.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_ignore_result=False
)