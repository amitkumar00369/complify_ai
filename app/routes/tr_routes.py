from fastapi import APIRouter, UploadFile, File
import zipfile
import os
import tempfile
from app.main import get_files
from ..controllers.tr_controller import process_tr

router = APIRouter()


@router.post("/upload-tr")
async def upload_tr(file: UploadFile = File(...)):

    results = []

    # create temp directory
    with tempfile.TemporaryDirectory() as tmp_dir:

        zip_path = os.path.join(tmp_dir, file.filename)

        # save uploaded zip
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        # extract zip
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmp_dir)

        # get all extracted files
        files = get_files(tmp_dir)

        for f_path in files:
            try:
                result = process_tr(f_path)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {f_path}: {e}")

    return {
        "total_files": len(results),
        "data": results
    }