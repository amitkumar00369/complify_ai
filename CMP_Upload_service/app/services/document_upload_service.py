
import uuid
import tempfile
import os
import aiofiles

from fastapi import (
    UploadFile
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

from app.services.s3_service import (
    s3_client
)

from app.services.document_job_service import (
    DocumentJobService
)

from core.config import (
    settings
)


class DocumentUploadService:

    @staticmethod
    async def upload_document(
        db,
        module,
        file: UploadFile
    ):

        temp_dir = None
        temp_file = None

        try:

            # ==============================
            # GENERATE JOB ID
            # ==============================
            parent_job_id = str(
                uuid.uuid4()
            )

            # ==============================
            # TEMP DIRECTORY
            # ==============================
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

            # ==============================
            # SAVE TEMP FILE
            # ==============================
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

            # ==============================
            # SHA256 HASH
            # ==============================
            file_hash = (
                HashUtil.generate_sha256(
                    temp_file
                )
            )

            # ==============================
            # DUPLICATE CHECK
            # ==============================
            existing_job = await (
                DocumentJobService.get_by_hash(
                    db,
                    file_hash
                )
            )

            if existing_job:

                return {

                    "success": False,

                    "message": (
                        "File already uploaded"
                    ),

                    "job_id": str(
                        existing_job.id
                    )
                }

            # ==============================
            # TOTAL FILES
            # ==============================
            if file.filename.lower().endswith(
                ".zip"
            ):

                total_files = (
                    FileCounter.count_valid_files(
                        temp_file
                    )
                )

            else:

                total_files = 1

            # ==============================
            # S3 RAW KEY
            # ==============================
            s3_key = (
                f"{module}/raw/{translated_name}"
            )

            # ==============================
            # UPLOAD TO S3
            # ==============================
            s3_client.upload_file(
                temp_file,
                settings.AWS_BUCKET_NAME,
                s3_key
            )

            # ==============================
            # CREATE DOCUMENT JOB
            # ==============================
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

                        "total_files":
                        total_files
                    }
                )
            )

            return {

                "success": True,

                "job_id": str(
                    job.id
                ),

                "status": job.status,

                "s3_key": s3_key,

                "total_files":
                total_files
            }

        finally:

            try:

                if (
                    temp_file
                    and
                    os.path.exists(
                        temp_file
                    )
                ):

                    os.remove(
                        temp_file
                    )

                if (
                    temp_dir
                    and
                    os.path.exists(
                        temp_dir
                    )
                ):

                    os.rmdir(
                        temp_dir
                    )

            except Exception:

                pass

