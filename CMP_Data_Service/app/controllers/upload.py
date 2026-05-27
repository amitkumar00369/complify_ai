import uuid
import tempfile
import os
import aiofiles

from fastapi import (
    UploadFile,
    File,
    Depends
)

from fastapi.responses import (
    JSONResponse
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from core.database import (
    get_db
)

from app.models.document_job import (
    DocumentJob
)

from app.utils.storage_service import (
    storage_service
)

from app.workers.parent_worker import (
    process_parent_zip
)

from app.utils.hash_util import (
    HashUtil
)

from app.services.document_job_service import (
    DocumentJobService
)

from app.utils.arbic_char import (
    SmartTranslator
)


# ==========================================
# UPLOAD DOCUMENT
# ==========================================
async def upload_document(
    module: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

    temp_dir = None
    temp_file = None

    try:

        # ==========================================
        # MODULE VALIDATION
        # ==========================================
        allowed_modules = [

            "items",

            "saleem",

            "saber",

            "standards",

            "technical-regulation",

            "hs-code"
        ]

        if module not in allowed_modules:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Invalid module"
                }
            )

        # ==========================================
        # FILE VALIDATION
        # ==========================================
        allowed_extensions = (

            ".zip",

            ".pdf",

            ".doc",

            ".docx",

            ".xlsx",

            ".xls",

            ".csv",

            ".png",

            ".jpg",

            ".jpeg"
        )

        if not file.filename.lower().endswith(
            allowed_extensions
        ):

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": (
                        "Invalid file type"
                    )
                }
            )

        # ==========================================
        # GENERATE JOB ID
        # ==========================================
        parent_job_id = str(
            uuid.uuid4()
        )

        # ==========================================
        # CREATE TEMP DIRECTORY
        # ==========================================
        temp_dir = tempfile.mkdtemp()

        translated_name = (
            SmartTranslator.smart_translate(
                file.filename
            )
        )

        temp_file = os.path.join(
            temp_dir,
            translated_name
        )

        # ==========================================
        # FILE SIZE CONFIG
        # ==========================================
        MAX_FILE_SIZE = (
            1000 * 1024 * 1024
        )  # 1000 MB

        CHUNK_SIZE = (
            1024 * 1024
        )  # 1 MB

        current_size = 0

        # ==========================================
        # STREAM FILE SAVE
        # ==========================================
        async with aiofiles.open(
            temp_file,
            "wb"
        ) as out_file:

            while chunk := await file.read(
                CHUNK_SIZE
            ):

                current_size += len(chunk)

                # ==================================
                # FILE SIZE VALIDATION
                # ==================================
                if current_size > MAX_FILE_SIZE:

                    await out_file.close()

                    if os.path.exists(
                        temp_file
                    ):

                        os.remove(
                            temp_file
                        )

                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": (
                                "File too large"
                            )
                        }
                    )

                await out_file.write(
                    chunk
                )

        # ==========================================
        # GENERATE FILE HASH
        # ==========================================
        file_hash = (
            HashUtil.generate_sha256(
                temp_file
            )
        )

        # ==========================================
        # CHECK DUPLICATE FILE
        # ==========================================
        existing_job = await (
            DocumentJobService.get_by_hash(
                db,
                file_hash
            )
        )

        if existing_job:

            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": (
                        "File already uploaded"
                    ),
                    "job_id": str(
                        existing_job.id
                    ),
                    "status": (
                        existing_job.status
                    )
                }
            )

        # ==========================================
        # STORE RAW FILE
        # ==========================================
        raw_path = (
            await storage_service.upload_file(
                temp_file,
                module,
                "raw",
                translated_name
            )
        )

        # ==========================================
        # CREATE PARENT JOB
        # ==========================================
        parent_job = DocumentJob(

            id=parent_job_id,

            module=module,

            file_name=translated_name,

            storage_path=raw_path,

            file_hash=file_hash,

            status="queued"
        )

        db.add(parent_job)

        await db.commit()

        await db.refresh(parent_job)

        # ==========================================
        # ZIP FILE -> PARENT WORKER
        # ==========================================
        if file.filename.lower().endswith(
            ".zip"
        ):

            process_parent_zip.delay(

                parent_job_id,

                module,

                raw_path
            )

        # ==========================================
        # SINGLE FILE -> CHILD WORKER
        # ==========================================
        else:

            from app.workers.child_worker import (
                process_child_file
            )

            process_child_file.delay(

                None,

                parent_job_id,

                module,

                raw_path,

                translated_name
            )

        # ==========================================
        # RESPONSE
        # ==========================================
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "job_id": parent_job_id,
                "status": "queued",
                "module": module
            }
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(e)
            }
        )

    finally:

        # ==========================================
        # CLEAN TEMP FILE
        # ==========================================
        try:

            if (
                temp_file
                and
                os.path.exists(temp_file)
            ):

                os.remove(
                    temp_file
                )

            if (
                temp_dir
                and
                os.path.exists(temp_dir)
            ):

                os.rmdir(
                    temp_dir
                )

        except Exception:

            pass