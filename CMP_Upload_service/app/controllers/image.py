import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import settings
from app.utils.s3 import s3_service

router = APIRouter(prefix="/upload", tags=["Upload"])


UPLOADS_DIR = "uploads"


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, "Only images allowed")

        # OPTION 1: LOCAL STORAGE (DEV)
        if settings.ENV == "dev":
            file_ext = file.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(UPLOADS_DIR, file_name)

            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            return {
                "message": "Uploaded locally",
                "url": f"http://localhost:4000/uploads/{file_name}"
            }

        #  OPTION 2: S3 (PRODUCTION)
        else:
            file_url = s3_service.upload_file(file)

            return {
                "message": "Uploaded to S3",
                "url": file_url
            }

    except Exception as e:
        raise HTTPException(500, str(e))