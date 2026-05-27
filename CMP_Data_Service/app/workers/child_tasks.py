from app.workers.celery_app import celery

from app.utils.tr_std_ksa_sbr_file_process import (
    process_ksa_saleem
)


@celery.task(
    bind=True,
    max_retries=3
)

def process_child_document(
    self,
    parent_job_id,
    file_path
):

    try:

        result = process_ksa_saleem(
            file_path
        )

        return {
            "status": "processed",
            "data": result
        }

    except Exception as e:

        raise self.retry(
            exc=e,
            countdown=10
        )