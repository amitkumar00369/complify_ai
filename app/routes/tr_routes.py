from fastapi import APIRouter, UploadFile, File
import zipfile
import os
import tempfile

from fastapi.responses import JSONResponse
from app.controllers.tr_controller import process_tr
from app.utils.zip_common import BASE_DIR, extract_zip, get_files
# BASE_DIR = "products_data"
    
router = APIRouter()
import uuid

@router.post("/upload-tr")
async def upload_tr(file: UploadFile = File(...)):

    results = []
    if not file.filename.endswith(".zip"):
        return JSONResponse({"error": "ZIP only"}, status_code=400)

    path = os.path.join(BASE_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    folder = extract_zip(path, "TR"+ case_id)
    files = get_files(folder)

    # create temp directory

        # get all extracted files
    # files = get_files(files)

    for f_path in files:
            try:
                result = process_tr(f_path)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {f_path}: {e}")
    with open("tr_results.json", "w") as f:
        import json
        json.dump(results, f, indent=2)
        
    

    return {
        "total_files": len(results),
        "data": results
    }