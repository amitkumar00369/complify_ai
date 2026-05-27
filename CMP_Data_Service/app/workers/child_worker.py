import os
import asyncio

from app.workers.celery_app import celery

from app.utils.storage_service import (
    storage_service
)
from core.database import (
    engine)
from app.services.processing_service import (
    ProcessingService
)

from app.services.document_job_item_service import (
    DocumentJobItemService
)

from app.services.document_job_service import (
    DocumentJobService
)



from core.database import (
    AsyncSessionLocal
)


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

            # ==================================
            # raw -> processing
            # ==================================
            processing_path = (
                await storage_service.move_file(
                    storage_path,
                    module,
                    "processing"
                )
            )

            # ==================================
            # UPDATE STORAGE PATH
            # ==================================
            await (
                DocumentJobItemService.update_storage_path(
                    db,
                    job_item_id,
                    processing_path
                )
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

            print("Processed Result:", result)

            # ==================================
            # SAVE BUSINESS DATA
            # ==================================
            # if module == "saleem":

            #     await (
            #         KSASaleemService.create_ksa(
            #             db,
            #             result
            #         )
            #     )

            # ==================================
            # processing -> processed
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
            await (
                DocumentJobItemService.update_status(
                    db,
                    job_item_id,
                    "completed"
                )
            )

            # ==================================
            # UPDATE STORAGE PATH
            # ==================================
            await (
                DocumentJobItemService.update_storage_path(
                    db,
                    job_item_id,
                    processed_path
                )
            )

            # ==================================
            # UPDATE PARENT COUNTS
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

            print(
                "Child Worker Error:",
                str(e)
            )

            # ==================================
            # processing -> failed
            # ==================================
            if (
                processing_path
                and
                os.path.exists(processing_path)
            ):

                failed_path = (
                    await storage_service.move_file(
                        processing_path,
                        module,
                        "failed"
                    )
                )

                await (
                    DocumentJobItemService.update_storage_path(
                        db,
                        job_item_id,
                        failed_path
                    )
                )

            # ==================================
            # UPDATE STATUS -> failed
            # ==================================
            await (
                DocumentJobItemService.update_status(
                    db,
                    job_item_id,
                    "failed",
                    str(e)
                )
            )

            # ==================================
            # RETRY COUNT
            # ==================================
            await (
                DocumentJobItemService.increment_retry_count(
                    db,
                    job_item_id
                )
            )

            # ==================================
            # UPDATE PARENT FAILED COUNT
            # ==================================
            await (
                DocumentJobService.increment_failed_files(
                    db,
                    parent_job_id
                )
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

        result = loop.run_until_complete(
            process_child_file_async(
                job_item_id,
                parent_job_id,
                module,
                storage_path,
                file_name
            )
        )

        return result

    except Exception as e:

        raise self.retry(
            exc=e,
            countdown=10
        )

    finally:

        # ==================================
        # CLOSE ALL DB CONNECTIONS
        # ==================================
        loop.run_until_complete(
            engine.dispose()
        )

        # ==================================
        # CLOSE LOOP
        # ==================================
        loop.close()