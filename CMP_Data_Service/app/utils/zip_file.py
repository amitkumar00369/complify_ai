

from PIL.ExifTags import Base
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import zipfile
import uuid

import shutil
import time



BASE_DIR = "products_data"
BASE_DIR1 = "Standard Data"
BASE_DIR2 = "Saber Data"
BASE_DIR3 = "KSA Data"
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(BASE_DIR1, exist_ok=True)
os.makedirs(BASE_DIR2, exist_ok=True)
os.makedirs(BASE_DIR3, exist_ok=True)

def extract_zip(zip_path, case_id):
    path = os.path.join(BASE_DIR, case_id)
    print("Extracting to:", path)
    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    return path

def extract_zip1(zip_path, case_id):
    path = os.path.join(BASE_DIR1, case_id)
    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    return path


def extract_zip2(zip_path, case_id):
    path = os.path.join(BASE_DIR2, case_id)
    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    return path


def extract_zip3(zip_path, case_id):
    path = os.path.join(BASE_DIR3, case_id)
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
def save_file(path: str, content: bytes):

    with open(path, "wb") as file:

        file.write(content)
        
        
def cleanup_file(path):

    if path and os.path.exists(path):

        os.remove(path)
        
def cleanup_folder(folder_path, retries=5, delay=1):

    if not folder_path or not os.path.exists(folder_path):
        return

    for attempt in range(retries):
        try:
            shutil.rmtree(folder_path)
            print(f"Deleted folder: {folder_path}")
            return

        except PermissionError as e:
            print(
                f"[Retry {attempt + 1}/{retries}] "
                f"Folder is busy: {e}"
            )

            time.sleep(delay)

        except Exception as e:
            print(f"Cleanup error: {e}")
            return

    print(f"Failed to delete folder after retries: {folder_path}")