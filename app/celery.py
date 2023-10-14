from celery import Celery

celery = Celery(
    'music_broadcast',
    broker="pyamqp://paxton:oolong20020222@localhost:5672//",
    backend="redis://localhost:6379/0",
    include=["app.task"]
)

celery.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"]
)