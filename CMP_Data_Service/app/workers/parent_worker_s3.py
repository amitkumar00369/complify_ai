
import os
import zipfile
import tempfile
import shutil
import asyncio

from core.database import (
    AsyncSessionLocal
)

from app.utils.s3_storage_service import (
    S3StorageService
)

from app.services.document_job_service import (
    DocumentJobService
)

from app.services.document_job_item_service import (
    DocumentJobItemService
)

from app.workers.child_worker import (
    process_child_file
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
    ".xls"
}


async def process_parent_zip_async(
    parent_job_id,
    module,
    s3_zip_key
):

    temp_dir = tempfile.mkdtemp()

    async with AsyncSessionLocal() as db:

        try:

            # ==================================
            # UPDATE STATUS
            # ==================================
            await (
                DocumentJobService.update_status(
                    db,
                    parent_job_id,
                    "processing"
                )
            )

            # ==================================
            # DOWNLOAD ZIP
            # ==================================
            local_zip = os.path.join(
                temp_dir,
                "source.zip"
            )

            await (
                S3StorageService.download_file(
                    s3_zip_key,
                    local_zip
                )
            )

            # ==================================
            # EXTRACT ZIP
            # ==================================
            extract_dir = os.path.join(
                temp_dir,
                "extract"
            )

            os.makedirs(
                extract_dir,
                exist_ok=True
            )

            with zipfile.ZipFile(
                local_zip,
                "r"
            ) as zip_ref:

                zip_ref.extractall(
                    extract_dir
                )

            extracted_files = []

            # ==================================
            # COLLECT FILES
            # ==================================
            for root, dirs, files in os.walk(
                extract_dir
            ):

                for file in files:

                    extension = (
                        os.path.splitext(file)[1]
                        .lower()
                    )

                    if (
                        extension
                        not in
                        ALLOWED_EXTENSIONS
                    ):

                        continue

                    extracted_files.append(
                        os.path.join(
                            root,
                            file
                        )
                    )

            # ==================================
            # UPDATE TOTAL FILES
            # ==================================
            await (
                DocumentJobService.update_total_files(
                    db,
                    parent_job_id,
                    len(extracted_files)
                )
            )

            # ==================================
            # PROCESS FILES
            # ==================================
            for local_file in extracted_files:

                file_name = os.path.basename(
                    local_file
                )

                raw_s3_key = (
                    f"{module}/raw/{file_name}"
                )

                # ==============================
                # UPLOAD TO RAW
                # ==============================
                await (
                    S3StorageService.upload_file(
                        local_file,
                        raw_s3_key
                    )
                )

                # ==============================
                # CREATE JOB ITEM
                # ==============================
                job_item = await (
                    DocumentJobItemService.create_job_item(
                        db,
                        {
                            "parent_job_id":
                            parent_job_id,

                            "module":
                            module,

                            "file_name":
                            file_name,

                            "storage_path":
                            raw_s3_key,

                            "status":
                            "queued"
                        }
                    )
                )

                # ==============================
                # QUEUE CHILD WORKER
                # ==============================
                process_child_file.delay(
                    str(job_item.id),
                    parent_job_id,
                    module,
                    raw_s3_key,
                    file_name
                )

            # ==================================
            # UPDATE STATUS
            # ==================================
            await (
                DocumentJobService.update_status(
                    db,
                    parent_job_id,
                    "queued"
                )
            )

        except Exception as e:

            await (
                DocumentJobService.update_status(
                    db,
                    parent_job_id,
                    "failed",
                    str(e)
                )
            )

            raise e

        finally:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )


def process_parent_zip(
    parent_job_id,
    module,
    s3_zip_key
):

    return asyncio.run(
        process_parent_zip_async(
            parent_job_id,
            module,
            s3_zip_key
        )
    )

