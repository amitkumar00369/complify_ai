

from app.utils.arbic_char import SmartTranslator

from concurrent.futures import ThreadPoolExecutor

from app.services.ocr_service import paddle_text
import fitz
import cv2
import numpy as np

def countDoc(file_path):
    doc = fitz.open(file_path)
    return doc.page_count
    

def extract_text_by_pages(file_path, start_page, end_page):



    doc = fitz.open(file_path)

    final_text = []

    for page_num in range(start_page - 1, end_page):

        page = doc[page_num]

        text = page.get_text().strip()

        # if no text → OCR
        if len(text) < 20:

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            img = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(pix.height, pix.width, pix.n)

            if pix.n == 4:
                img = cv2.cvtColor(
                    img,
                    cv2.COLOR_BGRA2BGR
                )

            text = paddle_text(img)

        final_text.append(text)

    doc.close()

    return "\n".join(final_text)