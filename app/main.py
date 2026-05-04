from .routes.tr_routes import router as tr_router





from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import zipfile
import uuid

from app.core.processor import process_documents

app = FastAPI()

BASE_DIR = "products_data"
os.makedirs(BASE_DIR, exist_ok=True)


def extract_zip(zip_path, case_id):
    path = os.path.join(BASE_DIR, case_id)
    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    return path


def get_files(folder):
    files = []
    for root, _, names in os.walk(folder):
        for name in names:
            if name.startswith("."):
                continue
            files.append(os.path.join(root, name))
    return files


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