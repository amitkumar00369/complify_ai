import uuid

import pdfplumber
import os

from app.services.image_service import extract_image
from ..services.pdf_service import extract_pdf
from ..services.ocr_service import paddle_text, tesseract_text
from ..services.hs_mapper import extract_hs_mapping

def process_tr(file_path):
    ext = file_path.lower()
    text, structured, method, conf = "", {}, "unknown", 0.0
    if ext.endswith(".pdf"):
        # import pdfplumber
        # tables = []

        # with pdfplumber.open(file_path) as pdf:
        #     for page in pdf.pages:
        #         tables = page.extract_tables()
        # print("Extracted tables:", len(tables),tables[:2])  # print first 2 tables for debugging
        text, structured, method, conf  = extract_pdf(file_path)
    elif ext.endswith((".png", ".jpg", ".jpeg")):
        text, structured, method, conf = extract_image(file_path)
    hs_mapping = extract_hs_mapping(text)
    # return {
    #         "total_standards": len(standards),
    #         "total_hs_codes": len(hs_codes),
    #         "standards": standards,
    #         "hs_codes": hs_codes
    #     }

    result = {
        "tr_id": str(uuid.uuid4()),
        "tr_name": file_path.split("/")[-1],
        "file_name": os.path.basename(file_path),
        "metaJson": {
            "total_standards": hs_mapping.get("total_standards", 0),
            "total_hs_codes": hs_mapping.get("total_hs_codes", 0),
            "standards": hs_mapping.get("standards", []),
            "hs_codes": hs_mapping.get("hs_codes", [])
        }
    }

    return result