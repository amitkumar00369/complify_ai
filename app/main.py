from app.utils.zip_common import extract_zip, get_files

from .routes.tr_routes import router as tr_router
from .routes.std_routes import router as std_router






from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import zipfile
import uuid

from app.core.processor import process_documents

app = FastAPI()

BASE_DIR = "products_data"






@app.post("/uploadCase")
async def upload_case(file: UploadFile = File(...)):
    #  how we know zipName
    hs_code = file.filename
    if not file.filename.endswith(".zip"):
        return JSONResponse({"error": "ZIP only"}, status_code=400)

    path = os.path.join(BASE_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    folder = extract_zip(path, case_id)
    files = get_files(folder)

    docs = process_documents(files, hs_code=hs_code)

    return {"case_id": case_id, "documents": docs}

app.include_router(tr_router, prefix="/tr", tags=["TR"])
app.include_router(std_router, prefix="/std", tags=["STD"])