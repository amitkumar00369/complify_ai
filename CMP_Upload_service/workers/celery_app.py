from celery import Celery

from core.config import settings


if settings.PROCESSING_MODE == "S3":

    worker_modules = [
        "app.workers.parent_worker_s3",
        "app.workers.child_worker_s3"
    ]

else:

    worker_modules = [
        "app.workers.parent_worker",
        "app.workers.child_worker"
    ]


celery = Celery(
    "document_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=worker_modules
)

celery.conf.update(

    task_serializer="json",

    accept_content=["json"],

    result_serializer="json",

    timezone="Asia/Kolkata",

    enable_utc=True,

    task_track_started=True,

    task_time_limit=3600,

    worker_prefetch_multiplier=1,

    task_acks_late=True,

    task_reject_on_worker_lost=True
)