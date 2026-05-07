from fastapi import APIRouter, UploadFile, File
import zipfile
import os
import tempfile

from fastapi.responses import JSONResponse
from app.controllers.tr_controller import process_std
from app.utils.zip_common import BASE_DIR, extract_zip2, get_files
# BASE_DIR = "products_data"
    
router = APIRouter()
import uuid

@router.post("/upload-std")
async def upload_std(file: UploadFile = File(...)):

    results = []
    if not file.filename.endswith(".zip"):
        return JSONResponse({"error": "ZIP only"}, status_code=400)

    path = os.path.join("Standard Data", file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    folder = extract_zip2(path, "STD"+ case_id)
    files = get_files(folder)

    # create temp directory

        # get all extracted files
    # files = get_files(files)

    for f_path in files:
            try:
                result = process_std(f_path)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {f_path}: {e}")
    with open("std_results.json", "w") as f:
        import json
        json.dump(results, f, indent=2)
        
    

    return {
        "total_files": len(results),
        "data": results
    }