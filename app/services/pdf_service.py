import fitz
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from ..services.ocr_service import paddle_text, tesseract_text
from ..services.visual_service import detect_visual_elements


# =========================
# SCANNED DETECTION
# =========================
def is_scanned(page):
    text = page.get_text().strip()
    images = page.get_images(full=True)

    # 🔥 improved logic
    if len(text) < 20 and len(images) > 0:
        return True

    if len(text) > 100:
        return False

    return len(text) < 30


# =========================
# PAGE PROCESSOR
# =========================
def process_page(page):
    try:
        scanned = is_scanned(page)

        #  if digital → no image rendering needed
        if not scanned:
            text_layer = page.get_text()

            # only run OCR if weak text
            if len(text_layer) > 100:
                return text_layer, {}

        #  render only when needed
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # =========================
        # OCR
        # =========================
        if scanned:
            text = tesseract_text(img)
        else:
            ocr_text = paddle_text(img)
            text_layer = page.get_text()
            text = ocr_text if len(ocr_text) > len(text_layer) else text_layer

        # =========================
        # VISUAL DETECTION
        # =========================
        visual = detect_visual_elements(img)

        return text, visual

    except Exception as e:
        print("Page error:", e)
        return "", {}


# =========================
# HELPER (NO FILE I/O)
# =========================


# =========================
# EXTRACT PDF (PARALLEL)
# =========================
def extract_pdf(file_path):
    # print(f"Processing PDF: {file_path}")   
    doc = fitz.open(file_path)

    texts = []
    visuals = {
        "logo": False,
        "stamp": False,
        "signature": False,
        "regions": []
    }

    #  PARALLEL EXECUTION
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_page, doc))

    for text, vis in results:
        texts.append(text)

        # merge visual results
        for k in ["logo", "stamp", "signature"]:
            visuals[k] = visuals[k] or vis.get(k, False)

        visuals["regions"].extend(vis.get("regions", []))

    doc.close()

    return "\n".join(texts), {"visual": visuals}, "pdf", 0.85