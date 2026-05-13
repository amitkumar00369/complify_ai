# from app.services.llama_service import databyhscode_usingllm
from app.utils.zip_common import extract_zip, get_files,save_file,cleanup_file,cleanup_folder

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






import os
import uuid
import aiofiles
import asyncio

from fastapi import UploadFile, File
from fastapi.responses import JSONResponse

# from app.common import (
#     BASE_DIR,
#     extract_zip,
#     get_files,
#     cleanup_file,
#     cleanup_folder
# )

@app.post("/uploadCase")
async def upload_case(
    file: UploadFile = File(...)
):

    folder = None

    try:

        zip_name = file.filename.split(".")[0]

        print(f"Received file: {file.filename}")

        if not file.filename.lower().endswith(
            (".zip", ".pdf")
        ):

            return JSONResponse(
                {"error": "ZIP and PDF only"},
                status_code=400
            )

        # =========================
        # FILE PATH
        # =========================
        path = os.path.join(
            BASE_DIR,
            file.filename
        )

        # =========================
        # SAVE FILE (STREAMING)
        # =========================
        async with aiofiles.open(path, "wb") as out_file:

            while chunk := await file.read(
                1024 * 1024
            ):

                await out_file.write(chunk)

        # =========================
        # CASE ID
        # =========================
        case_id = str(uuid.uuid4())[:8]

        # =========================
        # ZIP CHECK
        # =========================
        is_zip = file.filename.lower().endswith(
            ".zip"
        )

        # =========================
        # EXTRACT ZIP
        # =========================
        if is_zip:

            folder = await asyncio.to_thread(
                extract_zip,
                path,
                case_id
            )

            files = await asyncio.to_thread(
                get_files,
                folder
            )

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
        # LOAD OLD JSON
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

            product_name = item.get(
                "product_name"
            )

            existing_file_name = item.get(
                "file_name"
            )

            if product_name not in product_map:

                product_map[
                    product_name
                ] = {}

            product_map[
                product_name
            ][existing_file_name] = idx

        # =========================
        # MERGE LOGIC
        # =========================
        new_docs = []

        for doc in docs:

            product_name = doc.get(
                "product_name"
            )

            doc_file_name = doc.get(
                "file_name"
            )

            # PRODUCT EXISTS
            if product_name in product_map:

                # FILE EXISTS
                if doc_file_name in product_map[
                    product_name
                ]:

                    existing_index = product_map[
                        product_name
                    ][doc_file_name]

                    old_docs[
                        existing_index
                    ] = doc

                    new_docs.append(doc)

                # NEW FILE
                else:

                    old_docs.append(doc)

                    new_index = len(old_docs) - 1

                    product_map[
                        product_name
                    ][doc_file_name] = new_index

                    new_docs.append(doc)

            # NEW PRODUCT
            else:

                old_docs.append(doc)

                new_index = len(old_docs) - 1

                product_map[
                    product_name
                ] = {
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

    finally:

        # =========================
        # CLEANUP FILE
        # =========================
        await asyncio.to_thread(
            cleanup_file,
            path
        )

        # =========================
        # CLEANUP EXTRACTED FOLDER
        # =========================
        if folder:

            await asyncio.to_thread(
                cleanup_folder,
                folder
            )
@app.post("/uploadItem")
async def upload_item(
    file: UploadFile = File(...)
):

    folder = None
    path = None

    try:

        # =========================
        # VALIDATE FILE
        # =========================
        if not file.filename.lower().endswith(
            (".zip", ".pdf")
        ):

            return JSONResponse(
                {
                    "error": "ZIP and PDF only"
                },
                status_code=400
            )

        # =========================
        # UNIQUE FILE NAME
        # =========================
        unique_name = (
            f"{uuid.uuid4()}_{file.filename}"
        )

        zip_name = file.filename.split(".")[0]

        print(
            f"Received file: {file.filename}"
        )

        path = os.path.join(
            BASE_DIR,
            unique_name
        )

        # =========================
        # SAVE FILE (STREAMING) With Validation
        # =========================
        MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
        CHUNK_SIZE = 1024 * 1024           # 1 MB


        # =========================
        # SAVE FILE (STREAMING)
        # WITH FILE SIZE VALIDATION
        # =========================
        current_size = 0

        async with aiofiles.open(
            path,
            "wb"
        ) as out_file:

            while chunk := await file.read(CHUNK_SIZE):

                current_size += len(chunk)

                # =========================
                # FILE SIZE VALIDATION
                # =========================
                if current_size > MAX_FILE_SIZE:

                    # delete partial uploaded file
                    await out_file.close()

                    if os.path.exists(path):
                        os.remove(path)

                    return JSONResponse(
                        {
                            "error": (
                                "File too large. "
                                "Maximum allowed size is 500 MB"
                            )
                        },
                        status_code=400
                    )

                await out_file.write(chunk)

        # =========================
        # CASE ID
        # =========================
        case_id = str(uuid.uuid4())[:8]

        # =========================
        # ZIP CHECK
        # =========================
        is_zip = file.filename.lower().endswith(
            ".zip"
        )

        # =========================
        # EXTRACT ZIP
        # =========================
        if is_zip:

            try:

                folder = await asyncio.to_thread(
                    extract_zip,
                    path,
                    case_id
                )

            except zipfile.BadZipFile:

                return JSONResponse(
                    {
                        "error": "Invalid ZIP file"
                    },
                    status_code=400
                )

            files = await asyncio.to_thread(
                get_files,
                folder
            )

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

            product_name = item.get(
                "product_name"
            )

            existing_file_name = item.get(
                "file_name"
            )

            if product_name not in product_map:

                product_map[
                    product_name
                ] = {}

            product_map[
                product_name
            ][existing_file_name] = idx

        # =========================
        # MERGE LOGIC
        # =========================
        new_docs = []

        for doc in docs:

            product_name = doc.get(
                "product_name"
            )

            doc_file_name = doc.get(
                "file_name"
            )

            # PRODUCT EXISTS
            if product_name in product_map:

                # FILE EXISTS
                if doc_file_name in product_map[
                    product_name
                ]:

                    existing_index = product_map[
                        product_name
                    ][doc_file_name]

                    old_docs[
                        existing_index
                    ] = doc

                    new_docs.append(doc)

                # NEW FILE
                else:

                    old_docs.append(doc)

                    new_index = len(old_docs) - 1

                    product_map[
                        product_name
                    ][doc_file_name] = new_index

                    new_docs.append(doc)

            # NEW PRODUCT
            else:

                old_docs.append(doc)

                new_index = len(old_docs) - 1

                product_map[
                    product_name
                ] = {
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

    except Exception as e:

        return JSONResponse(
            {
                "error": str(e)
            },
            status_code=500
        )

    finally:

        # =========================
        # CLEANUP UPLOADED FILE
        # =========================
        if path:

            await asyncio.to_thread(
                cleanup_file,
                path
            )

        # =========================
        # CLEANUP EXTRACTED FOLDER
        # =========================
        if folder:

            await asyncio.to_thread(
                cleanup_folder,
                folder
            )
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