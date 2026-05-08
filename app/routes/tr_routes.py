from fastapi import APIRouter, UploadFile, File
import zipfile
import os
import tempfile

from fastapi.responses import JSONResponse
from pydantic import json
from app.controllers.tr_controller import process_tr
from app.utils.zip_common import BASE_DIR, extract_zip, get_files
# BASE_DIR = "products_data"
    
router = APIRouter()
import uuid

# @router.post("/upload-tr")
# async def upload_tr(file: UploadFile = File(...)):

#     results = []
#     if not file.filename.endswith(".zip"):
#         return JSONResponse({"error": "ZIP only"}, status_code=400)

#     path = os.path.join(BASE_DIR, file.filename)

#     with open(path, "wb") as f:
#         f.write(await file.read())

#     case_id = str(uuid.uuid4())[:8]

#     folder = extract_zip(path, "TR"+ case_id)
#     files = get_files(folder)

#     # create temp directory

#         # get all extracted files
#     # files = get_files(files)

#     for f_path in files:
#             try:
#                 result = process_tr(f_path)
#                 if result:
#                     results.append(result)
#             except Exception as e:
#                 print(f"Error processing {f_path}: {e}")
#     with open("tr_results.json", "w") as f:
#         import json
#         json.dump(results, f, indent=2)
        
    

#     return {
#         "total_files": len(results),
#         "data": results
#     }


@router.post("/upload-tr")
async def upload_tr(file: UploadFile = File(...)):

    import json

    json_path = "tr_results.json"

    # -----------------------------
    # Load existing JSON
    # -----------------------------
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            results = json.load(f)
    else:
        results = []

    # existing unique file names
    existing_files = {
        item.get("file_name")
        for item in results
    }

    if not file.filename.endswith(".zip"):
        return JSONResponse(
            {"error": "ZIP only"},
            status_code=400
        )

    path = os.path.join(BASE_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    folder = extract_zip(path, "TR" + case_id)
    files = get_files(folder)

    # -----------------------------
    # Process files
    # -----------------------------
    for f_path in files:
        try:

            result = process_tr(f_path)

            if not result:
                continue

            file_name = result.get("file_name")

            # skip duplicate
            if file_name in existing_files:
                print(f"Duplicate skipped: {file_name}")
                continue

            existing_files.add(file_name)

            results.append(result)

        except Exception as e:
            print(f"Error processing {f_path}: {e}")

    # -----------------------------
    # Save updated JSON
    # -----------------------------
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    return {
        "total_files": len(results),
        "data": results
    }
    
@router.get("/get-tr")
async def get_tr():

    import json

    json_path = "tr_results.json"

    if os.path.exists(json_path):

        print(f"Loading TR results from {json_path}...")

        with open(json_path, "r", encoding="utf-8") as f:

            print(
                f"size of TR results file: "
                f"{os.path.getsize(json_path)} bytes"
            )

            try:
                data = json.load(f)

            except Exception as e:

                print("JSON ERROR:", str(e))

                # debug corrupted content
                f.seek(0)
                print(f.read()[:500])

                data = []

    else:
        data = []

    return {
        "total_items": len(data),
        "data": data
    }