import uuid

from app.services.image_service import extract_image
from ..services.pdf_service import extract_pdf
from ..services.ocr_service import paddle_text, tesseract_text
from ..services.hs_mapper import extract_hs_mapping

def process_tr(file_path):
    ext = file_path.lower()
    text, structured, method, conf = "", {}, "unknown", 0.0
    if ext.endswith(".pdf"):
        text, structured, method, conf  = extract_pdf(file_path)
    elif ext.endswith((".png", ".jpg", ".jpeg")):
        text, structured, method, conf = extract_image(file_path)
    hs_mapping = extract_hs_mapping(text)

    result = {
        "tr_id": str(uuid.uuid4()),
        "tr_name": file_path.split("/")[-1],
        "metaJson": {
            "hs_mapping": hs_mapping
        }
    }

    return result