from fastapi import APIRouter
uploadFileRouter: APIRouter = APIRouter()

from app.controllers.upload import upload_zip
uploadFileRouter.post("/upload")(upload_zip)