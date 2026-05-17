from app.services.pdf_service import extract_pdf

from app.utils.extract_word import extract_word_file
import asyncio

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
            # text, structured, method, conf = extract_image(file_path)
            # continue
            return "", {},ext.endswith, 0.0
        elif ext.endswith((".doc", ".docx")):

            text, structured, method, conf = extract_word_file(file_path)
        

        # =========================
        # EXCEL
        # =========================
        elif ext.endswith((".csv", ".xls", ".xlsx")):
            # text, structured, method, conf = extract_excel(file_path)
            return "", {},ext.endswith, 0.0

        # =========================
        # UNKNOWN
        # =========================
        return "", {}, "unknown", 0.0

    except Exception as e:
        print("Extractor error:", e)
        return "", {}, "failed", 0.0