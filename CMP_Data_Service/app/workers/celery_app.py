from celery import Celery

celery = Celery(
    "document_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "app.workers.parent_worker",
        "app.workers.child_worker"
    ]
)

celery.conf.update(

    task_serializer="json",

    accept_content=["json"],

    result_serializer="json",

    timezone="Asia/Kolkata",

    enable_utc=True,

    task_track_started=True,

    task_time_limit=3600,

    worker_prefetch_multiplier=1
)