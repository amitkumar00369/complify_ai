import os
import zipfile
import uuid
import hashlib
import fitz
import pandas as pd
import tempfile
import cv2
import numpy as np
import pytesseract
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR

# =========================
# CONFIG
# =========================
BASE_DIR = "products_data"
DEBUG_DIR = "ocr_debug"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_use_pir_api"] = "0"

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# 🔥 optimized OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')


# =========================
# UTILS
# =========================
def generate_sha256(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None


def normalize_text(text):
    import re
    text = text.lower()
    text = re.sub(r'javascript:\S+', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def validate_text(text):
    if not text or len(text) < 30:
        return False, ["too_short"]
    keywords = ["voltage", "frequency", "test", "report", "certificate"]
    if not any(k in text for k in keywords):
        return True, ["low_signal"]
    return True, []


def validate_file(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


# =========================
# OCR (OPTIMIZED)
# =========================
def safe_ocr_image(img):
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = ocr.ocr(img_rgb)

        text = ""
        confs = []

        if result:
            for line in result:
                for word in line:
                    text += word[1][0] + " "
                    confs.append(word[1][1])

        avg = sum(confs)/len(confs) if confs else 0.0
        return text.strip(), avg
    except:
        return "", 0.0


# 🔥 reduced OCR passes
def multi_ocr(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    t1, c1 = safe_ocr_image(img)

    big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    t2, c2 = safe_ocr_image(big)

    return (t1, c1) if len(t1) > len(t2) else (t2, c2)


def safe_ocr(file_path):
    img = cv2.imread(file_path)
    return multi_ocr(img)


# =========================
# VISUAL DETECTION (LIMITED)
# =========================
def get_candidate_regions(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    H, W = gray.shape[:2]

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h

        if area < 2000 or area > (H * W * 0.15):
            continue

        regions.append((x, y, w, h))

    return regions


def detect_visual_elements(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return {"logo": False, "stamp": False, "signature": False, "regions": []}

    regions = get_candidate_regions(img)

    # 🔥 LIMIT regions (BIG SPEED BOOST)
    regions = sorted(regions, key=lambda x: x[2]*x[3], reverse=True)[:5]

    result = {"logo": False, "stamp": False, "signature": False, "regions": []}

    for (x, y, w, h) in regions:
        crop = img[y:y+h, x:x+w]

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges) / (h * w)

        if 0.02 < edge_density < 0.2:
            result["signature"] = True
        elif edge_density > 0.2:
            result["stamp"] = True

    return result


# =========================
# PDF PROCESSING (PARALLEL 🚀)
# =========================
def process_page(page):
    try:
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)

        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # reduced DPI
        pix.save(tmp)

        img = cv2.imread(tmp)

        kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
        img = cv2.filter2D(img, -1, kernel)

        text, conf = multi_ocr(img)
        vis = detect_visual_elements(tmp)

        os.remove(tmp)

        return text, conf, vis

    except Exception as e:
        print("Page error:", e)
        return "", 0.0, {}


def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
    except:
        return "", "failed", 0.0, {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_page, doc))

    full_text = []
    total_conf = 0
    visual_data = {"logo": False, "stamp": False, "signature": False, "regions": []}

    for text, conf, vis in results:
        full_text.append(text)
        total_conf += conf

        for k in ["logo", "stamp", "signature"]:
            visual_data[k] = visual_data[k] or vis.get(k, False)

    doc.close()

    avg_conf = total_conf / len(results) if results else 0.0

    return "\n".join(full_text), "mixed", avg_conf, visual_data


# =========================
# UNIVERSAL EXTRACTOR
# =========================
def extract_text_from_file(file_path):
    ext = file_path.lower()

    if ext.endswith(".pdf"):
        text, method, conf, visual = extract_text_from_pdf(file_path)
        return text, {"visual": visual}, method, conf

    elif ext.endswith((".png", ".jpg", ".jpeg")):
        text, conf = safe_ocr(file_path)
        visual = detect_visual_elements(file_path)
        return text, {"visual": visual}, "ocr", conf

    elif ext.endswith((".csv", ".xls", ".xlsx")):
        df = pd.read_excel(file_path)
        text = df.astype(str).apply(lambda x: " ".join(x), axis=1).str.cat(sep="\n")
        return text, {}, "structured", 1.0

    elif ext.endswith(".txt"):
        with open(file_path, "r", errors="ignore") as f:
            return f.read(), {}, "text", 1.0

    return "", {}, "unknown", 0.0


# =========================
# MAIN PIPELINE
# =========================
def process_documents(files):
    documents = []

    for file in files:
        if not validate_file(file):
            continue

        raw_text, _, method, conf = extract_text_from_file(file)

        clean_text = normalize_text(raw_text)
        is_valid, flags = validate_text(clean_text)

        documents.append({
            "file_path": file,
            "confidence": conf,
            "status": "VERIFIED" if conf > 0.5 else "FAILED",
            "flags": flags,
            "method": method
        })

    return documents


# =========================
# ZIP HANDLING
# =========================
def extract_zip(zip_path, case_id):
    path = os.path.join(BASE_DIR, case_id)
    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    return path


def get_all_files(folder):
    files = []
    for root, _, names in os.walk(folder):
        for name in names:
            if name.startswith("."):
                continue
            files.append(os.path.join(root, name))
    return files


# =========================
# API
# =========================
@app.post("/uploadCase")
async def upload_case(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        return JSONResponse({"success": False, "message": "Only ZIP allowed"}, status_code=400)

    path = os.path.join(BASE_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    case_id = str(uuid.uuid4())[:8]

    extract_path = extract_zip(path, case_id)
    files = get_all_files(extract_path)

    documents = process_documents(files)

    return JSONResponse({
        "success": True,
        "data": {
            "case_id": case_id,
            "documents": documents,
            "total_files": len(files)
        }
    })