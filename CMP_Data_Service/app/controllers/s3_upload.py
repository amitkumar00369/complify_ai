
import uuid
import tempfile
import os
import aiofiles

from app.utils.file_counter import FileCounter
from fastapi import (
    APIRouter,
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

from app.utils.hash_util import (
    HashUtil
)

from app.utils.arbic_char import (
    SmartTranslator
)

from app.services.document_job_service import (
    DocumentJobService
)

from app.utils.s3_storage_service import (
    S3StorageService
)

from app.workers.parent_worker import (
    process_parent_zip
)

from app.workers.child_worker import (
    process_child_file
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

        # ==================================
        # SAVE TEMP FILE
        # ==================================
        async with aiofiles.open(
            temp_file,
            "wb"
        ) as out_file:

            while chunk := await file.read(
                1024 * 1024
            ):

                await out_file.write(
                    chunk
                )

        # ==================================
        # FILE HASH
        # ==================================
        file_hash = (
            HashUtil.generate_sha256(
                temp_file
            )
        )

        # ==================================
        # JOB ID
        # ==================================
        parent_job_id = str(
            uuid.uuid4()
        )

        # ==================================
        # S3 RAW KEY
        # ==================================
        s3_key = (
            f"{module}/raw/{translated_name}"
        )

        # ==================================
        # UPLOAD TO S3
        # ==================================
        await (
            S3StorageService.upload_file(
                temp_file,
                s3_key
            )
        )
        if translated_name.lower().endswith( ".zip" ): 
            total_files = ( FileCounter.count_valid_files( temp_file ) ) 
        else:
            total_files = 1

        # ==================================
        # CREATE JOB
        # ==================================
        job = await (
            DocumentJobService.create_job(
                db,
                {
                    "id": parent_job_id,
                    "module": module,
                    "file_name":
                    translated_name,
                    "s3_key": s3_key,
                    "file_hash":
                    file_hash,
                    "total_files": total_files
                }
            )
        )

        # ==================================
        # ROUTE WORKER
        # ==================================
        if translated_name.lower().endswith(
            ".zip"
        ):

            process_parent_zip.delay(
                parent_job_id,
                module,
                s3_key
            )

        else:

            process_child_file.delay(
                None,
                parent_job_id,
                module,
                s3_key,
                translated_name
            )

        return {
            "success": True,
            "job_id": str(job.id),
            "status": "queued"
        }

    finally:

        if os.path.exists(temp_file):

            os.remove(temp_file)

        if os.path.exists(temp_dir):

            os.rmdir(temp_dir)

