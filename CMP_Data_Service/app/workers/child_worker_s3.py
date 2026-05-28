
import os
import asyncio
import tempfile
from datetime import datetime

from core.database import (
    AsyncSessionLocal
)

from app.utils.s3_storage_service import (
    S3StorageService
)

from app.services.processing_service import (
    ProcessingService
)

from app.services.document_job_item_service import (
    DocumentJobItemService
)

from app.services.document_job_service import (
    DocumentJobService
)


async def process_child_file_async(
    job_item_id,
    parent_job_id,
    module,
    s3_key,
    file_name
):

    temp_dir = tempfile.mkdtemp()

    async with AsyncSessionLocal() as db:

        try:

            # ==================================
            # UPDATE STATUS
            # ==================================
            await (
                DocumentJobItemService.update_status(
                    db,
                    job_item_id,
                    "processing"
                )
            )

            processing_key = s3_key.replace(
                "/raw/",
                "/processing/"
            )

            processed_key = s3_key.replace(
                "/raw/",
                "/processed/"
            )

            failed_key = s3_key.replace(
                "/raw/",
                "/failed/"
            )

            # ==================================
            # ARCHIVE OLD FILE
            # ==================================
            exists = await (
                S3StorageService.file_exists(
                    processed_key
                )
            )

            if exists:

                timestamp = (
                    datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )
                )

                archived_key = (
                    processed_key.replace(
                        "/processed/",
                        f"/archived/{timestamp}_"
                    )
                )

                await (
                    S3StorageService.move_file(
                        processed_key,
                        archived_key
                    )
                )

            # ==================================
            # RAW -> PROCESSING
            # ==================================
            await (
                S3StorageService.move_file(
                    s3_key,
                    processing_key
                )
            )

            # ==================================
            # DOWNLOAD LOCAL FILE
            # ==================================
            local_path = os.path.join(
                temp_dir,
                file_name
            )

            await (
                S3StorageService.download_file(
                    processing_key,
                    local_path
                )
            )

            # ==================================
            # UPDATE STORAGE PATH
            # ==================================
            await (
                DocumentJobItemService.update_storage_path(
                    db,
                    job_item_id,
                    processing_key
                )
            )

            # ==================================
            # PROCESS DOCUMENT
            # ==================================
            await (
                ProcessingService.process_document(
                    module,
                    local_path
                )
            )

            # ==================================
            # PROCESSING -> PROCESSED
            # ==================================
            await (
                S3StorageService.move_file(
                    processing_key,
                    processed_key
                )
            )

            # ==================================
            # UPDATE STATUS
            # ==================================
            await (
                DocumentJobItemService.update_status(
                    db,
                    job_item_id,
                    "completed"
                )
            )

            await (
                DocumentJobItemService.update_storage_path(
                    db,
                    job_item_id,
                    processed_key
                )
            )

            # ==================================
            # UPDATE COUNTS
            # ==================================
            await (
                DocumentJobService.increment_processed_files(
                    db,
                    parent_job_id
                )
            )

            return {
                "success": True
            }

        except Exception as e:

            # ==================================
            # MOVE TO FAILED
            # ==================================
            try:

                await (
                    S3StorageService.move_file(
                        processing_key,
                        failed_key
                    )
                )

            except Exception:
                pass

            # ==================================
            # UPDATE STATUS
            # ==================================
            await (
                DocumentJobItemService.update_status(
                    db,
                    job_item_id,
                    "failed",
                    str(e)
                )
            )

            await (
                DocumentJobItemService.increment_retry_count(
                    db,
                    job_item_id
                )
            )

            await (
                DocumentJobService.increment_failed_files(
                    db,
                    parent_job_id
                )
            )

            raise e

        finally:

            if os.path.exists(temp_dir):

                import shutil

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )


def process_child_file(
    job_item_id,
    parent_job_id,
    module,
    s3_key,
    file_name
):

    return asyncio.run(
        process_child_file_async(
            job_item_id,
            parent_job_id,
            module,
            s3_key,
            file_name
        )
    )

