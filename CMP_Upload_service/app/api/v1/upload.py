from fastapi import APIRouter
uploadFileRouter: APIRouter = APIRouter()

from app.controllers.upload import upload_document ,upload_multiple_files
from app.controllers.s3_upload import  upload_document_on_s3
uploadFileRouter.post("/upload")(upload_document)
uploadFileRouter.post("/upload_on_s3")(upload_document_on_s3)
uploadFileRouter.post("/uploadFiles")(upload_multiple_files)
