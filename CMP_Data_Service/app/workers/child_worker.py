
import os
import shutil
import asyncio

from datetime import datetime

from core.database import (
    engine,
    AsyncSessionLocal
)

from app.workers.celery_app import celery

from app.utils.storage_service import (
    storage_service
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


# ==========================================
# TRANSIENT ERRORS
# ==========================================
TRANSIENT_ERRORS = [
    "connection",
    "timeout",
    "temporarily",
    "deadlock",
    "event loop",
    "closed",
    "send",
    "connection reset"
]


# ==========================================
# MOVE FILE TO FAILED
# ==========================================
def move_to_failed_sync(
    processing_path,
    module
):

    if (
        not processing_path
        or
        not os.path.exists(processing_path)
    ):

        return None

    failed_dir = os.path.join(
        "storage",
        module,
        "failed"
    )

    os.makedirs(
        failed_dir,
        exist_ok=True
    )

    failed_path = os.path.join(
        failed_dir,
        os.path.basename(processing_path)
    )

    shutil.move(
        processing_path,
        failed_path
    )

    print(
        f"Moved file to failed folder: "
        f"{failed_path}"
    )

    return failed_path


# ==========================================
# ASYNC CHILD PROCESSOR
# ==========================================
async def process_child_file_async(
    job_item_id,
    parent_job_id,
    module,
    storage_path,
    file_name
):

    processing_path = None

    async with AsyncSessionLocal() as db:

        try:

            # ==================================
            # UPDATE STATUS -> processing
            # ==================================
            await (
                DocumentJobItemService.update_status(
                    db,
                    job_item_id,
                    "processing"
                )
            )

            filename = os.path.basename(
                storage_path
            )

            raw_candidate = os.path.join(
                "storage",
                module,
                "raw",
                filename
            )

            processing_candidate = os.path.join(
                "storage",
                module,
                "processing",
                filename
            )

            processed_candidate = os.path.join(
                "storage",
                module,
                "processed",
                filename
            )

            failed_candidate = os.path.join(
                "storage",
                module,
                "failed",
                filename
            )

            # ==================================
            # RETRY CASE
            # ==================================
            if os.path.exists(
                processing_candidate
            ):

                print(
                    f"Retry detected: "
                    f"{processing_candidate}"
                )

                processing_path = (
                    processing_candidate
                )

            # ==================================
            # DUPLICATE FILE CASE
            # ==================================
            elif os.path.exists(
                processed_candidate
            ):

                print(
                    f"Processed file exists. "
                    f"Archiving old file."
                )

                timestamp = (
                    datetime.now().strftime(
                        "%Y%m%d_%H%M%S"
                    )
                )

                archived_name = (
                    f"{os.path.splitext(filename)[0]}"
                    f"_{timestamp}"
                    f"{os.path.splitext(filename)[1]}"
                )

                archived_destination = os.path.join(
                    "storage",
                    module,
                    "archived",
                    archived_name
                )

                os.makedirs(
                    os.path.dirname(
                        archived_destination
                    ),
                    exist_ok=True
                )

                await storage_service.move_existing_file(
                    processed_candidate,
                    archived_destination
                )

                if os.path.exists(
                    raw_candidate
                ):

                    processing_path = (
                        await storage_service.move_file(
                            raw_candidate,
                            module,
                            "processing"
                        )
                    )

                else:

                    raise FileNotFoundError(
                        f"Raw file missing: {filename}"
                    )

            # ==================================
            # NORMAL FLOW
            # ==================================
            elif os.path.exists(
                raw_candidate
            ):

                processing_path = (
                    await storage_service.move_file(
                        raw_candidate,
                        module,
                        "processing"
                    )
                )

            # ==================================
            # FAILED RETRY
            # ==================================
            elif os.path.exists(
                failed_candidate
            ):

                processing_path = (
                    failed_candidate
                )

            # ==================================
            # FILE NOT FOUND
            # ==================================
            else:

                raise FileNotFoundError(
                    f"File missing: {filename}"
                )

            # ==================================
            # UPDATE STORAGE PATH
            # ==================================
            try:

                await (
                    DocumentJobItemService.update_storage_path(
                        db,
                        job_item_id,
                        processing_path
                    )
                )

            except Exception as db_error:

                print(
                    "Failed updating storage path:",
                    str(db_error)
                )

            # ==================================
            # PROCESS DOCUMENT
            # ==================================
            result = await (
                ProcessingService.process_document(
                    module,
                    processing_path
                )
            )

            print(
                "Processed Result:",
                result
            )

            # ==================================
            # MOVE TO PROCESSED
            # ==================================
            processed_path = (
                await storage_service.move_file(
                    processing_path,
                    module,
                    "processed"
                )
            )

            # ==================================
            # UPDATE STATUS -> completed
            # ==================================
            try:

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
                        processed_path
                    )
                )

                await (
                    DocumentJobService.increment_processed_files(
                        db,
                        parent_job_id
                    )
                )

            except Exception as db_error:

                print(
                    "DB update error after processing:",
                    str(db_error)
                )

            return {
                "success": True
            }

        except Exception as e:

            print(
                "Child Worker Error:",
                str(e)
            )

            failed_path = None

            # ==================================
            # MOVE TO FAILED
            # ==================================
            try:

                failed_path = move_to_failed_sync(
                    processing_path,
                    module
                )

            except Exception as move_error:

                print(
                    "Failed moving file:",
                    str(move_error)
                )

            # ==================================
            # UPDATE FAILED STATUS
            # ==================================
            try:

                await (
                    DocumentJobItemService.update_status(
                        db,
                        job_item_id,
                        "failed",
                        str(e)
                    )
                )

                if failed_path:

                    await (
                        DocumentJobItemService.update_storage_path(
                            db,
                            job_item_id,
                            failed_path
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

            except Exception as db_error:

                print(
                    "Failed updating DB after error:",
                    str(db_error)
                )

            raise e


# ==========================================
# CELERY ENTRY
# ==========================================
@celery.task(
    bind=True,
    max_retries=3
)
def process_child_file(
    self,
    job_item_id,
    parent_job_id,
    module,
    storage_path,
    file_name
):

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:

        return loop.run_until_complete(
            process_child_file_async(
                job_item_id,
                parent_job_id,
                module,
                storage_path,
                file_name
            )
        )

    except FileNotFoundError as e:

        print(
            "Permanent file error:",
            str(e)
        )

        raise e

    except Exception as e:

        error_message = str(e).lower()

        print(
            "Task Exception:",
            error_message
        )

        should_retry = any(
            transient_error in error_message
            for transient_error in TRANSIENT_ERRORS
        )

        if should_retry:

            print(
                "Retrying transient failure..."
            )

            raise self.retry(
                exc=e,
                countdown=10
            )

        print(
            "Permanent failure. No retry."
        )

        raise e

    finally:

        try:

            loop.run_until_complete(
                engine.dispose()
            )

        except Exception as dispose_error:

            print(
                "Engine dispose error:",
                str(dispose_error)
            )

        loop.close()

