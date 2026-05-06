

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import zipfile
import uuid





BASE_DIR = "products_data"
BASE_DIR1 = "Standard Data"
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(BASE_DIR1, exist_ok=True)

def extract_zip(zip_path, case_id):
    path = os.path.join(BASE_DIR, case_id)
    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    return path

def extract_zip1(zip_path, case_id):
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
