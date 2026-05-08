from fastapi import APIRouter, UploadFile, File
import zipfile
import os
import tempfile
import json
from fastapi.responses import JSONResponse
from app.controllers.tr_controller import process_ksa_saleem, process_ksa_saleem, process_saber, process_std
from app.utils.zip_common import BASE_DIR, extract_zip1, extract_zip3, get_files
BASE_DIR ="KSA Data"
    
router = APIRouter()
import uuid

@router.post("/upload-ksa-saleem")
async def upload_saber(file: UploadFile = File(...)):

    results = []
    if not file.filename.endswith(".zip"):
        return JSONResponse({"error": "ZIP only"}, status_code=400)

    path = os.path.join(BASE_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    folder = extract_zip3(path, "KSA"+ case_id)
    files = get_files(folder)

    # create temp directory

        # get all extracted files
    # files = get_files(files)

    for f_path in files:
            try:
                result = process_ksa_saleem(f_path)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {f_path}: {e}")
    with open("ksa_saleem.json", "w") as f:
        json.dump(results, f, indent=2)
        
    return {
        "total_files": len(results),
        "data": results
    }