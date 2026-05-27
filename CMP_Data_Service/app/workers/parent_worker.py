import os
import zipfile
import tempfile

from app.services.document_job_item_service import (
    DocumentJobItemService
)

from app.services.queue_service import (
    queue_service
)

from app.services.s3_service import (
    s3_service
)


async def process_zip_job(
    db,
    parent_job,
    local_zip_path
):

    extract_dir = tempfile.mkdtemp()

    # extract zip
    with zipfile.ZipFile(
        local_zip_path,
        "r"
    ) as zip_ref:

        zip_ref.extractall(extract_dir)

    # loop extracted files
    for root, dirs, files in os.walk(
        extract_dir
    ):

        for file in files:

            local_file_path = os.path.join(
                root,
                file
            )

            # upload extracted file to s3
            s3_key = (
                f"{parent_job.module}/raw/"
                f"{parent_job.id}/{file}"
            )

            await s3_service.upload_local_file(
                local_file_path,
                s3_key
            )

            # create child item
            item = (
                await DocumentJobItemService.create_item(
                    db,
                    {
                        "parent_job_id": parent_job.id,
                        "module": parent_job.module,
                        "file_name": file,
                        "original_file_name": file,
                        "s3_key": s3_key,
                        "file_size": os.path.getsize(
                            local_file_path
                        )
                    }
                )
            )

            # push queue
            await queue_service.publish(
                {
                    "job_item_id": str(item.id),
                    "module": parent_job.module,
                    "s3_key": s3_key
                }
            )