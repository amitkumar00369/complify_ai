
import os
import zipfile
import tempfile
import asyncio
import shutil

from core.database import (
    engine
)

from app.workers.celery_app import (
    celery
)

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
# ALLOWED FILES
# ==========================================
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
    ".xls"
}


# ==========================================
# VALIDATE ZIP PATH
# ==========================================
def is_safe_path(
    base_path,
    target_path
):

    abs_base = os.path.abspath(
        base_path
    )

    abs_target = os.path.abspath(
        target_path
    )

    return abs_target.startswith(
        abs_base
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
            # EXTRACT ZIP SAFELY
            # ==================================
            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as zip_ref:

                for member in zip_ref.namelist():

                    member_path = os.path.join(
                        extract_dir,
                        member
                    )

                    if not is_safe_path(
                        extract_dir,
                        member_path
                    ):

                        raise Exception(
                            "Unsafe ZIP content detected"
                        )

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

                    # ==========================
                    # SKIP HIDDEN FILES
                    # ==========================
                    if file.startswith(
                        "."
                    ):

                        continue

                    local_file = os.path.join(
                        root,
                        file
                    )

                    extension = os.path.splitext(
                        file
                    )[1].lower()

                    # ==========================
                    # SKIP UNSUPPORTED FILES
                    # ==========================
                    if (
                        extension
                        not in
                        ALLOWED_EXTENSIONS
                    ):

                        print(
                            f"Skipping unsupported file: "
                            f"{file}"
                        )

                        continue

                    extracted_files.append(
                        local_file
                    )

            # ==================================
            # NO VALID FILES
            # ==================================
            if not extracted_files:

                raise Exception(
                    "No valid files found in ZIP"
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

                try:

                    file = os.path.basename(
                        local_file
                    )

                    print(
                        f"Uploading file: {file}"
                    )

                    # ==========================
                    # STORE RAW FILE
                    # ==========================
                    destination = (
                        await storage_service.upload_file(
                            local_file,
                            module,
                            "raw",
                            file
                        )
                    )

                    print(
                        f"Stored raw file: "
                        f"{destination}"
                    )

                    # ==========================
                    # CREATE JOB ITEM
                    # ==========================
                    job_item = await (
                        DocumentJobItemService.create_job_item(
                            db,
                            {
                                "parent_job_id":
                                parent_job_id,

                                "module":
                                module,

                                "file_name":
                                file,

                                "storage_path":
                                destination,

                                "status":
                                "queued"
                            }
                        )
                    )

                    print(
                        "Created Job Item:",
                        job_item.id
                    )

                    # ==========================
                    # COMMIT BEFORE QUEUE
                    # ==========================
                    await db.commit()

                    # ==========================
                    # QUEUE CHILD TASK
                    # ==========================
                    process_child_file.delay(
                        str(job_item.id),
                        parent_job_id,
                        module,
                        destination,
                        file
                    )

                except Exception as file_error:

                    print(
                        f"Failed processing file "
                        f"{local_file}: "
                        f"{str(file_error)}"
                    )

            # ==================================
            # UPDATE STATUS -> queued
            # ==================================
            await (
                DocumentJobService.update_status(
                    db,
                    parent_job_id,
                    "queued"
                )
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
                os.path.exists(
                    extract_dir
                )
            ):

                shutil.rmtree(
                    extract_dir,
                    ignore_errors=True
                )


# ==========================================
# CELERY ENTRYPOINT
# ==========================================
# @celery.task
# def process_parent_zip(
#     parent_job_id,
#     module,
#     zip_path
# ):

#     try:

#         return asyncio.run(
#             process_parent_zip_async(
#                 parent_job_id,
#                 module,
#                 zip_path
#             )
#         )

#     finally:

#         asyncio.run(
#             engine.dispose()
#         )


@celery.task
def process_parent_zip(
    parent_job_id,
    module,
    zip_path
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(
            process_parent_zip_async(
                parent_job_id,
                module,
                zip_path
            )
        )

    finally:
        loop.run_until_complete(engine.dispose())
        loop.close()
