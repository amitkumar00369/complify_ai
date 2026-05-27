import os
import zipfile
import tempfile
import asyncio
import shutil
from core.database import (
    engine)

from app.workers.celery_app import celery

from app.utils.storage_service import (
    storage_service
)

from app.workers.child_worker import (
    process_child_file
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
# ASYNC LOGIC
# ==========================================
async def process_parent_zip_async(
    parent_job_id,
    module,
    zip_path
):

    extract_dir = None

    async with AsyncSessionLocal() as db:

        try:

            # ==================================
            # UPDATE STATUS -> processing
            # ==================================
            await (
                DocumentJobService.update_status(
                    db,
                    parent_job_id,
                    "processing"
                )
            )

            # ==================================
            # VALIDATE ZIP
            # ==================================
            if not zipfile.is_zipfile(
                zip_path
            ):

                raise Exception(
                    "Invalid ZIP file"
                )

            # ==================================
            # TEMP EXTRACT DIR
            # ==================================
            extract_dir = tempfile.mkdtemp()

            # ==================================
            # EXTRACT ZIP
            # ==================================
            with zipfile.ZipFile(
                zip_path,
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

                    local_file = os.path.join(
                        root,
                        file
                    )

                    extracted_files.append(
                        local_file
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
            # LOOP FILES
            # ==================================
            for local_file in extracted_files:

                file = os.path.basename(
                    local_file
                )

                # ==============================
                # STORE RAW FILE
                # ==============================
                destination = (
                    await storage_service.upload_file(
                        local_file,
                        module,
                        "raw",
                        file
                    )
                )

                # ==============================
                # CREATE JOB ITEM
                # ==============================
                job_item = await (
                    DocumentJobItemService.create_job_item(
                        db,
                        {
                            "parent_job_id": (
                                parent_job_id
                            ),

                            "module": module,

                            "file_name": file,

                            "storage_path": (
                                destination
                            ),

                            "status": "queued"
                        }
                    )
                )

                print(
                    "Created Job Item:",
                    job_item.id
                )

                # ==============================
                # QUEUE CHILD TASK
                # ==============================
                process_child_file.delay(
                    str(job_item.id),
                    parent_job_id,
                    module,
                    destination,
                    file
                )

        except Exception as e:

            print(
                "Parent Worker Error:",
                str(e)
            )

            # ==================================
            # UPDATE STATUS -> failed
            # ==================================
            await (
                DocumentJobService.update_status(
                    db,
                    parent_job_id,
                    "failed",
                    str(e)
                )
            )

        finally:

            # ==================================
            # CLEAN TEMP DIR
            # ==================================
            if (
                extract_dir
                and
                os.path.exists(extract_dir)
            ):

                shutil.rmtree(
                    extract_dir,
                    ignore_errors=True
                )


# ==========================================
# CELERY ENTRYPOINT
# ==========================================
@celery.task
def process_parent_zip(
    parent_job_id,
    module,
    zip_path
):

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:

        result = loop.run_until_complete(
            process_parent_zip_async(
                parent_job_id,
                module,
                zip_path
            )
        )

        return result

    finally:

        # ==================================
        # CLOSE DB CONNECTIONS
        # ==================================
        loop.run_until_complete(
            engine.dispose()
        )

        # ==================================
        # CLOSE LOOP
        # ==================================
        loop.close()