# from app.services.llama_service import databyhscode_usingllm
from app.utils.zip_common import extract_zip, get_files,save_file

from .routes.tr_routes import router as tr_router
from .routes.std_routes import router as std_router
from .routes.saber import router as saber_router
from .routes.ksa_saleem import router as ksa_saleem_router
from app.routes.query_routes import router as query_router
from app.utils.jsonFilesHandles import load_json_file,save_json_file
import json




from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import zipfile
import uuid
import asyncio
from app.core.processor import process_documents
from app.core.newProcess import process_item_documents

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
    
@app.post("/uploadItem")
async def upload_item(file: UploadFile = File(...)):

    zip_name = file.filename.split(".")[0]

    print(f"Received file: {file.filename}")

    if not file.filename.endswith((".zip",".pdf")):

        return JSONResponse(
            {"error": "ZIP and pdf  only"},
            status_code=400
        )

    path = os.path.join(
        BASE_DIR,
        file.filename
    )

    # =========================
    # SAVE ZIP FILE
    # =========================
    content = await file.read()

    await asyncio.to_thread(
        save_file,
        path,
        content
    )

    # =========================
    # CASE ID
    # =========================
    case_id = str(uuid.uuid4())[:8]

    # =========================
    # EXTRACT ZIP
    # =========================
    is_zip = file.filename.lower().endswith(".zip")

    if is_zip:

        folder = await asyncio.to_thread(
            extract_zip,
            path,
            case_id
        )

        files = get_files(folder)

    else:

        files = [path]
        

    # =========================
    # PROCESS DOCUMENTS
    # =========================
    docs = await process_item_documents(
        files,
        file_name=zip_name
    )

    json_path = "items.json"

    # =========================
    # LOAD EXISTING JSON
    # =========================
    old_docs = await asyncio.to_thread(
        load_json_file,
        json_path
    )

    # =========================
    # BUILD PRODUCT MAP
    # =========================
    product_map = {}

    for idx, item in enumerate(old_docs):

        product_name = item.get("product_name")

        existing_file_name = item.get("file_name")

        if product_name not in product_map:

            product_map[product_name] = {}

        product_map[product_name][existing_file_name] = idx

    # =========================
    # MERGE LOGIC
    # =========================
    new_docs = []

    for doc in docs:

        product_name = doc.get("product_name")

        doc_file_name = doc.get("file_name")

        # PRODUCT EXISTS
        if product_name in product_map:

            # FILE EXISTS -> REPLACE
            if doc_file_name in product_map[product_name]:

                existing_index = product_map[
                    product_name
                ][doc_file_name]

                old_docs[existing_index] = doc

                new_docs.append(doc)

            # NEW FILE INSIDE PRODUCT
            else:

                old_docs.append(doc)

                new_index = len(old_docs) - 1

                product_map[product_name][
                    doc_file_name
                ] = new_index

                new_docs.append(doc)

        # NEW PRODUCT
        else:

            old_docs.append(doc)

            new_index = len(old_docs) - 1

            product_map[product_name] = {
                doc_file_name: new_index
            }

            new_docs.append(doc)

    # =========================
    # SAVE JSON
    # =========================
    await asyncio.to_thread(
        save_json_file,
        json_path,
        old_docs
    )

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
@app.get("/getHSCodeData")
async def get_hs_code_data(data: dict):
    payload = data.get("hs_code")
    if not payload:
        return JSONResponse({"error": "HS code is required"}, status_code=400)
    # result  = databyhscode_usingllm(payload)
    return {
        "result": "result"
    }
    


    
app.include_router(tr_router, prefix="/tr", tags=["TR"])
app.include_router(std_router, prefix="/std", tags=["STD"])
app.include_router(saber_router, prefix="/saber", tags=["SABER"])
app.include_router(ksa_saleem_router, prefix="/ksa-saleem", tags=["KSA_SALEEM"])
app.include_router(query_router, prefix="/compliance", tags=["QUERY"])