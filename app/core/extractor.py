from ..services.pdf_service import extract_pdf
from ..services.image_service import extract_image
from ..services.excel_service import extract_excel


def extract_text(file_path):
    ext = file_path.lower()

    try:
        # =========================
        # PDF
        # =========================
        if ext.endswith(".pdf"):
            text, structured, method, conf = extract_pdf(file_path)
            return text, structured, method, conf

        # =========================
        # IMAGE
        # =========================
        elif ext.endswith((".png", ".jpg", ".jpeg")):
            text, structured, method, conf = extract_image(file_path)
            return text, structured, method, conf

        # =========================
        # EXCEL
        # =========================
        elif ext.endswith((".csv", ".xls", ".xlsx")):
            text, structured, method, conf = extract_excel(file_path)
            return text, structured, method, conf

        # =========================
        # UNKNOWN
        # =========================
        return "", {}, "unknown", 0.0

    except Exception as e:
        print("Extractor error:", e)
        return "", {}, "failed", 0.0