import uuid
import tempfile
import os
import aiofiles
from fastapi import UploadFile, File
from typing import List
import tempfile
import re

import re
import os

def clean_filename(filename: str):

    name, ext = os.path.splitext(filename)

    name = re.sub(
        r"[^\w\s-]",
        "",
        name
    )

    name = re.sub(
        r"[\s_]+",
        "-",
        name
    )

    name = re.sub(
        r"-+",
        "-",
        name
    )

    return f"{name.strip('-')}{ext.lower()}"

from app.utils.file_counter import FileCounter
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
from datetime import datetime
# from app.workers.parent_worker import (
#     process_parent_zip
# )

from app.utils.hash_util import (
    HashUtil
)

from app.services.document_job_service import (
    DocumentJobService
)

from app.utils.arbic_char import (
    SmartTranslator
)
from app.utils.enum import (
    allowedModules,allowedExtensions,subFolderModule
)
from core.config import settings
allowed_extensions = (

            allowedExtensions.zip,

            allowedExtensions.pdf ,

            allowedExtensions.doc,

            allowedExtensions.docx ,

            allowedExtensions.xlsx ,

            allowedExtensions.xls ,

            allowedExtensions.csv,

            allowedExtensions.png,

            allowedExtensions.jpg,

            allowedExtensions.jpeg
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
            allowedModules.saleem,
            allowedModules.saber,
            allowedModules.saber_cases,
            allowedModules.standards,
            allowedModules.technical_regulation,
            allowedModules.hs_code
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

        # ==========================================
        # GENERATE FILE HASH
        # ==========================================
        file_hash = (
            HashUtil.generate_sha256(
                temp_file
            )
        )
        if file.filename.lower().endswith(allowedExtensions.zip):
            total_files = FileCounter.count_valid_files(
                temp_file
            )
        else:
            total_files = 1

        # # ==========================================
        # # CHECK DUPLICATE FILE
        # # ==========================================
        # existing_job = await (
        #     DocumentJobService.get_by_hash(
        #         db,
        #         file_hash
        #     )
        # )

        # if existing_job:

        #     return JSONResponse(
        #         status_code=200,
        #         content={
        #             "success": False,
        #             "message": (
        #                 "File already uploaded"
        #             ),
        #             "job_id": str(
        #                 existing_job.id
        #             ),
        #             "status": (
        #                 existing_job.status
        #             )
        #         }
        #     )

        # ==========================================
        # STORE RAW FILE
        # ==========================================
        raw_path = (
            await storage_service.upload_file(
                temp_file,
                module,
                subFolderModule.raw,
                translated_name
            )
        )
        

        # ==========================================
        # CREATE JOB
        parent_job = await DocumentJobService.create_job(
            db,
            {
                "id": parent_job_id,
                "module": module,
                "file_name": translated_name,
                "s3_key": raw_path,
                "file_hash": file_hash,
                "total_files": total_files
            }
        )
        print("Parent Job Created:", parent_job)

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "job_id": parent_job_id,
                "data": parent_job,
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
        

def generate_case_number(case_id: int) -> str:
    return f"CASE{case_id:08d}"
async def upload_multiple_files(
    files: List[UploadFile] = File(...)
):
    try:

        uploaded_files = []
        caseId = generate_case_number(1)    #12 digit case id with case00000000
        print("caseId" ,caseId)
        timestamp = int(datetime.now().timestamp())
        print("timestamp",timestamp)
        

        for file in files:

            # ==========================================
            # FILE TYPE VALIDATION
            # ==========================================
            if not file.filename.lower().endswith(
                allowed_extensions
            ):
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": (
                            f"Invalid file type: {file.filename}"
                        )
                    }
                )

            # ==========================================
            # GENERATE JOB ID
            # ==========================================

            # ==========================================
            # CREATE TEMP DIRECTORY
            # ==========================================
            temp_dir = tempfile.mkdtemp()

            translated_name = (
                SmartTranslator.smart_translate(
                    file.filename
                )
            )
            translated_name = clean_filename(translated_name)
            userType = "user"
            filestructure = f"{caseId}-{userType}-{timestamp}-{translated_name}"
            print("filestructure type", type(filestructure))
            print(f"raw/{filestructure.lower()}")

            temp_file = os.path.join(
                temp_dir,
                translated_name
            )

            # ==========================================
            # FILE SIZE CONFIG
            # ==========================================
            MAX_FILE_SIZE = settings.FILE_SIZE_LIMIT
            CHUNK_SIZE = settings.CHUNK_SIZE

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

                    # ==============================
                    # FILE SIZE VALIDATION
                    # ==============================
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
                                    f"File too large: {file.filename}"
                                )
                            }
                        )

                    await out_file.write(
                        chunk
                    )

            uploaded_files.append(
                {
                    "job_id": caseId,
                    "filename": translated_name,
                    "path": temp_file,
                    "size": current_size
                }
            )

            # Upload to S3
            # Create DB record
            # Send SQS message

        return {
            "success": True,
            "total_files": len(uploaded_files),
            "files": uploaded_files
        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(e)
            }
        )