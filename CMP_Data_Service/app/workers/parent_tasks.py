import os
import zipfile
import tempfile

from app.workers.celery_app import celery

from app.workers.child_tasks import (
    process_child_document
)


@celery.task

def process_zip_job(
    parent_job_id,
    zip_path
):

    extract_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_ref:

        zip_ref.extractall(
            extract_dir
        )

    for root, dirs, files in os.walk(
        extract_dir
    ):

        for file in files:

            full_path = os.path.join(
                root,
                file
            )

            # create child task
            process_child_document.delay(
                parent_job_id,
                full_path
            )

    return {
        "status": "zip processed"
    }