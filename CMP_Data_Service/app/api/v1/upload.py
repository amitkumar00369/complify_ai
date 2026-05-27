from fastapi import APIRouter
uploadFileRouter: APIRouter = APIRouter()

from app.controllers.upload import upload_document
uploadFileRouter.post("/upload")(upload_document)