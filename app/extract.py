from paddleocr import PaddleOCR
import fitz
import pandas as pd
import os

ocr = PaddleOCR(use_angle_cls=True, lang='en')


def extract_text_from_file(file_path):
    ext = file_path.lower()

    try:
        # ======================
        # 1️⃣ PDF HANDLING (TEXT + IMAGE)
        # ======================
        if ext.endswith(".pdf"):
            text = ""
            doc = fitz.open(file_path)

            for page_num, page in enumerate(doc):

                # 🔹 1. Extract text layer
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"

                # 🔹 2. Extract images inside PDF
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    img_path = f"temp_img_{page_num}_{img_index}.png"

                    with open(img_path, "wb") as f:
                        f.write(image_bytes)

                    # OCR on extracted image
                    ocr_result = ocr.ocr(img_path)

                    if ocr_result:
                        for line in ocr_result[0]:
                            text += line[1][0] + "\n"

                    os.remove(img_path)

                # 🔹 3. If NO text → full page OCR (scanned PDF)
                if not page_text.strip():
                    pix = page.get_pixmap()
                    img_path = f"temp_page_{page_num}.png"
                    pix.save(img_path)

                    ocr_result = ocr.ocr(img_path)

                    if ocr_result:
                        for line in ocr_result[0]:
                            text += line[1][0] + "\n"

                    os.remove(img_path)

            return text


        # ======================
        # 2️⃣ IMAGE FILE
        # ======================
        elif ext.endswith((".png", ".jpg", ".jpeg")):
            result = ocr.ocr(file_path)
            text = ""

            if result:
                for line in result[0]:
                    text += line[1][0] + "\n"

            return text


        # ======================
        # 3️⃣ EXCEL
        # ======================
        elif ext.endswith(".xlsx"):
            df = pd.read_excel(file_path)
            return df.to_string()


        # ======================
        # 4️⃣ TXT
        # ======================
        elif ext.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()


        # ======================
        # 5️⃣ UNKNOWN
        # ======================
        return ""

    except Exception as e:
        print("Extraction error:", e)
        return ""