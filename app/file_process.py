# ocr_engine.py

import os
os.environ["FLAGS_use_mkldnn"] = "0"   # 🔥 disable OneDNN (fix crash)
os.environ["FLAGS_use_pir_api"] = "0"  # 🔥 avoid PIR issues

import cv2
import numpy as np
import fitz  # PyMuPDF
import tempfile

from paddleocr import PaddleOCR
import pytesseract
# import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize once
ocr = PaddleOCR(use_angle_cls=True, lang='en')


# -----------------------------
# IMAGE PREPROCESSING
# -----------------------------
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=25)  # contrast boost
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


# -----------------------------
# PADDLE OCR
# -----------------------------
def paddle_ocr(img):
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = ocr.ocr(img_rgb)

        text = []
        if result:
            for line in result:
                if line:
                    for word in line:
                        text.append(word[1][0])

        return " ".join(text).strip()
    except Exception as e:
        print("Paddle OCR error:", e)
        return ""


# -----------------------------
# TESSERACT FALLBACK
# -----------------------------
def tesseract_ocr(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text.strip()
    except Exception as e:
        print("Tesseract error:", e)
        return ""


# -----------------------------
# MULTI-OCR (ROBUST)
# -----------------------------
def run_ocr(img):
    # resize for better detection
    img_big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    img_proc = preprocess(img_big)

    text = paddle_ocr(img_proc)

    # 🔥 fallback if paddle fails
    if not text:
        print("⚠️ Paddle failed → using Tesseract fallback")
        text = tesseract_ocr(img_proc)

    return text


# -----------------------------
# PDF → TEXT
# -----------------------------
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)

    all_text = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))

        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        pix.save(tmp)

        img = cv2.imread(tmp)

        # check text layer first
        text_layer = page.get_text().strip()

        if len(text_layer) > 20:
            print(f"[Page {i}] using text layer")
            all_text.append(text_layer)
        else:
            print(f"[Page {i}] using OCR")
            ocr_text = run_ocr(img)
            all_text.append(ocr_text)

        try:
            os.remove(tmp)
        except:
            pass

    doc.close()

    return "\n".join(all_text).strip()


# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import JSONResponse
# import os
# import uuid

# from ocr_engine import extract_text_from_pdf

# app = FastAPI()

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# @app.post("/ocr-pdf")
# async def ocr_pdf(file: UploadFile = File(...)):
#     if not file.filename.endswith(".pdf"):
#         return JSONResponse({"error": "Only PDF allowed"}, status_code=400)

#     file_id = str(uuid.uuid4())[:8]
#     file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     try:
#         text = extract_text_from_pdf(file_path)

#         return {
#             "success": True,
#             "file": file.filename,
#             "text_length": len(text),
#             "text": text[:2000]  # preview
#         }

#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)