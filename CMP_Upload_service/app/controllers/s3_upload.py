import uuid
import tempfile
import shutil
import os
import aiofiles
from core.config import settings

from fastapi import (
    UploadFile,
    File,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from core.database import (
    get_db
)

from app.services.s3_service import (
    s3_service
)

from app.services.sqs_service import (
    sqs_service
)

from app.services.document_job_service import (
    DocumentJobService
)

from app.utils.hash_util import (
    HashUtil
)

from app.utils.arbic_char import (
    SmartTranslator
)

from app.utils.file_counter import (
    FileCounter
)
from fastapi.responses import (
    JSONResponse
)


async def upload_document_on_s3(
    module: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

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

    try:

        # FILE SIZE CONFIG
        # ==========================================
        MAX_FILE_SIZE = settings.FILE_SIZE_LIMIT

        CHUNK_SIZE = (
            settings.CHUNK_SIZE
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

        # ==================================
        # GENERATE HASH
        # ==================================
        file_hash = (
            HashUtil.generate_sha256(
                temp_file
            )
        )

        # ==================================
        # CREATE JOB ID
        # ==================================
        parent_job_id = str(
            uuid.uuid4()
        )

        # ==================================
        # GENERATE S3 KEY
        # ==================================
        s3_key = (
            f"{module}/raw/{translated_name}"
        )

        # ==================================
        # UPLOAD TO S3
        # ==================================
        await s3_service.upload_file(
            temp_file,
            s3_key
        )

        # ==================================
        # COUNT FILES
        # ==================================
        total_files = (
            FileCounter.count_valid_files(
                temp_file
            )
            if translated_name.lower().endswith(
                ".zip"
            )
            else 1
        )

        # ==================================
        # CREATE JOB
        # ==================================
        parent_job = await (
            DocumentJobService.create_job(
                db,
                {
                    "id":
                    parent_job_id,

                    "module":
                    module,

                    "file_name":
                    translated_name,

                    "s3_key":
                    s3_key,

                    "file_hash":
                    file_hash,

                    "status":
                    "queued",

                    "total_files":
                    total_files
                }
            )
        )

        # ==================================
        # PUBLISH SQS EVENT
        # ==================================
        try:

            await (
                sqs_service.publish_document_uploaded(
                    {
                        "job_id":
                        parent_job_id,

                        "module":
                        module,

                        "s3_key":
                        s3_key,

                        "file_name":
                        translated_name
                    }
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

            raise Exception(
                f"SQS Publish Failed: {str(e)}"
            )

        # ==================================
        # SUCCESS RESPONSE
        # ==================================
        return {
            "success": True,
            "job_id": parent_job_id,
            "status": "queued",
            "s3_key": s3_key
        }

    except Exception as e:

        raise e

    finally:

        # ==================================
        # CLEAN TEMP FILES
        # ==================================
        if os.path.exists(
            temp_dir
        ):

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )