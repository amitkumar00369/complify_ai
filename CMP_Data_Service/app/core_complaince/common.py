import hashlib
import os
import re

import fitz
import pandas as pd
from PIL import Image

def sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def normalize(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def validate(text):
    if len(text) < 30:
        return False
    return True





def valid_file(file_path):

    try:

        # =========================
        # BASIC CHECK
        # =========================
        if not os.path.exists(file_path):
            return False

        if os.path.getsize(file_path) == 0:
            return False

        ext = file_path.lower()

        # =========================
        # PDF
        # =========================
        if ext.endswith(".pdf"):

            doc = fitz.open(file_path)

            if doc.page_count == 0:
                return False

            # validate rendering
            page = doc[0]
            pix = page.get_pixmap()

            if pix.width == 0 or pix.height == 0:
                return False

            doc.close()

            return True

        # =========================
        # IMAGE
        # =========================
        elif ext.endswith((".png", ".jpg", ".jpeg")):

            img = Image.open(file_path)

            img.verify()

            return True
        elif ext.endswith((".doc", ".docx")):
            pass
            

        

        # =========================
        # CSV
        # =========================
        elif ext.endswith(".csv"):

            df = pd.read_csv(file_path, nrows=5)

            return True

        # =========================
        # EXCEL
        # =========================
        elif ext.endswith((".xls", ".xlsx")):

            df = pd.read_excel(file_path, nrows=5)

            return True

        # =========================
        # TXT
        # =========================
        elif ext.endswith(".txt"):

            with open(file_path, "r", encoding="utf-8") as f:
                f.read(100)

            return True

        # =========================
        # UNKNOWN
        # =========================
        return False

    except Exception as e:

        print("File validation error:", e)

        return False

# def find_hs_code(text):
#     #  simple regex for HS code (6-10 digits)
#      # example  843850000002
#     match = re.search(r'\b\d{6,10}\b', text)
#     return match.group(0) if match else None