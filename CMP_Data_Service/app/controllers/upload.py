from fastapi import (
    APIRouter,
    UploadFile,
    File
)

import uuid
import os

from app.workers.parent_tasks import (
    process_zip_job
)



async def upload_zip(
    file: UploadFile = File(...)
):

    parent_job_id = str(uuid.uuid4())

    upload_path = (
        f"temp/{parent_job_id}_{file.filename}"
    )

    with open(upload_path, "wb") as f:

        content = await file.read()

        f.write(content)

    # push celery task
    process_zip_job.delay(
        parent_job_id,
        upload_path
    )

    return {
        "job_id": parent_job_id,
        "status": "queued"
    }