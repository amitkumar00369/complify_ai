from app.utils.zip_common import extract_zip, get_files

from .routes.tr_routes import router as tr_router
from .routes.std_routes import router as std_router
from .routes.saber import router as saber_router
from .routes.ksa_saleem import router as ksa_saleem_router
from app.routes.query_routes import router as query_router

import json




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
    file_name = file.filename.split(".")[0]
    print(f"Received file: {file.filename}")
    if not file.filename.endswith(".zip"):
        return JSONResponse({"error": "ZIP only"}, status_code=400)

    path = os.path.join(BASE_DIR, file.filename)
    # zip name
    # file_name = file.filename.split(".")[0]

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    folder = extract_zip(path, case_id)
    files = get_files(folder)

    docs = process_documents(files, file_name=file_name)
    json_path = "items.json"

    # OLD DATA LOAD
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                old_docs = json.load(f)
            except:
                old_docs = []
    else:
        old_docs = []

    # EXISTING FILE NAMES
    existing_files = {
        item.get("file_name")
        for item in old_docs
    }

    # ONLY NEW UNIQUE DOCS
    new_docs = []

    for doc in docs:

        file_name = doc.get("file_name")

        if file_name not in existing_files:
            new_docs.append(doc)
            existing_files.add(file_name)

    # MERGE
    old_docs.extend(new_docs)

    # SAVE
    with open(json_path, "w") as f:
        json.dump(old_docs, f, indent=4)

    return {
        "case_id": case_id,
        "new_documents": new_docs,
        "total_documents": len(old_docs)
    }
@app.get("/getProducts")
async def get_products():
    json_path = "items.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                docs = json.load(f)
            except:
                docs = []
    else:
        docs = []

    return {
        "total_products": len(docs),
        "products": docs
    }
app.include_router(tr_router, prefix="/tr", tags=["TR"])
app.include_router(std_router, prefix="/std", tags=["STD"])
app.include_router(saber_router, prefix="/saber", tags=["SABER"])
app.include_router(ksa_saleem_router, prefix="/ksa-saleem", tags=["KSA_SALEEM"])
app.include_router(query_router, prefix="/compliance", tags=["QUERY"])