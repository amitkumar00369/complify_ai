import os
import zipfile
import uuid
import re
import hashlib
import fitz
import pandas as pd
import tempfile
import time
DEBUG_DIR = "ocr_debug"
os.makedirs(DEBUG_DIR, exist_ok=True)
import cv2
import numpy as np

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR

app = FastAPI()

BASE_DIR = "products_data"
os.makedirs(BASE_DIR, exist_ok=True)

ocr = PaddleOCR(use_angle_cls=True, lang='en')
def debug_ocr_pipeline(img, page_num):
    try:
        base_name = f"page_{page_num}"

        # 1. original
        orig_path = os.path.join(DEBUG_DIR, base_name + "_original.png")
        cv2.imwrite(orig_path, img)

        # 2. resized
        resized = cv2.resize(img, None, fx=2, fy=2)
        resized_path = os.path.join(DEBUG_DIR, base_name + "_resized.png")
        cv2.imwrite(resized_path, resized)

        # 3. grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_path = os.path.join(DEBUG_DIR, base_name + "_gray.png")
        cv2.imwrite(gray_path, gray)

        # 4. enhanced
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=20)
        enhanced_path = os.path.join(DEBUG_DIR, base_name + "_enhanced.png")
        cv2.imwrite(enhanced_path, enhanced)

        # convert for OCR
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        # 🔥 OCR run
        result = ocr.ocr(enhanced_bgr)

        debug_img = enhanced_bgr.copy()

        text_log = []

        if result:
            for line in result:
                for word in line:
                    text = word[1][0]
                    conf = word[1][1]
                    box = word[0]

                    text_log.append(f"{text} ({conf:.2f})")

                    # draw box
                    pts = np.array(box, dtype=np.int32)
                    cv2.polylines(debug_img, [pts], True, (0,255,0), 2)

        # save bounding box image
        bbox_path = os.path.join(DEBUG_DIR, base_name + "_bbox.png")
        cv2.imwrite(bbox_path, debug_img)

        # save text output
        txt_path = os.path.join(DEBUG_DIR, base_name + "_text.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(text_log))

        print(f"DEBUG saved for page {page_num}")

    except Exception as e:
        print("Debug OCR error:", e)


# =========================
# UTILS
# =========================
def generate_sha256(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None


# def normalize_text(text):
def normalize_text(text):
    import re

    text = text.lower()

    # remove javascript garbage
    text = re.sub(r'javascript:\S+', '', text)

    # remove urls
    text = re.sub(r'http\S+', '', text)

    # remove weird symbols
    text = re.sub(r'[^a-z0-9\s\.\-:/]', ' ', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def validate_text(text):
    if not text or len(text) < 30:
        return False, ["too_short"]
    keywords = ["voltage", "frequency", "test", "report", "certificate", "declaration"]
    if not any(k in text for k in keywords):
        return True, ["low_signal"]
    return True, []


def validate_file(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


# =========================
# OCR (STRONGER FOR SCANNED)
# =========================
def preprocess_image_for_ocr(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        out = image_path + "_proc.png"
        cv2.imwrite(out, thresh)
        return out
    except:
        return image_path


def safe_ocr(image_path):
    try:
        img = cv2.imread(image_path)

        # 🔥 resize (very important)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # contrast improve
        gray = cv2.equalizeHist(gray)

        # adaptive threshold (better than fixed)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        result = ocr.ocr(thresh)

        text = ""
        confs = []

        if result and len(result) > 0:
            for line in result[0]:
                text += line[1][0] + "\n"
                confs.append(line[1][1])

        avg_conf = sum(confs) / len(confs) if confs else 0.0

        return text, avg_conf

    except:
        return "", 0.0


def safe_ocr_crop(img_crop):
    try:
        result = ocr.ocr(img_crop)
        text = ""
        confs = []
        if result and len(result) > 0:
            for line in result[0]:
                text += line[1][0] + "\n"
                confs.append(line[1][1])
        avg = sum(confs) / len(confs) if confs else 0.0
        return text, avg
    except:
        return "", 0.0


# =========================
# REGION-BASED VISUAL DETECTION (LAYOUT-AGNOSTIC)
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

        # 🔥 stricter filtering
        if area < 2000:
            continue
        if area > (H * W * 0.15):   # पहले 0.5 था (बहुत बड़ा)
            continue

        # ignore very long strips
        aspect_ratio = w / float(h)
        if aspect_ratio > 10 or aspect_ratio < 0.1:
            continue

        regions.append((x, y, w, h))

    return regions

def is_blue_stamp(crop):
    try:
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([90, 60, 60])
        upper_blue = np.array([140, 255, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        blue_ratio = np.sum(mask > 0) / (crop.shape[0] * crop.shape[1])

        # 🔥 stricter threshold
        if blue_ratio < 0.15:
            return False

        # circular check
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            1, 50,
            param1=50, param2=30,
            minRadius=20, maxRadius=200
        )

        return circles is not None

    except:
        return False


def is_signature_like(crop):
    try:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        density = np.sum(edges) / (crop.shape[0] * crop.shape[1])

        # 🔥 tighter range
        if density < 0.01 or density > 0.08:
            return False

        # width > height → signature-like
        h, w = gray.shape
        if w < h:
            return False

        return True

    except:
        return False


def is_logo_like(crop):
    try:
        text, conf = safe_ocr_crop(crop)

        h, w, _ = crop.shape
        area = h * w

        # logo size range
        if area < 3000 or area > 50000:
            return False

        # OCR based
        if conf > 0.5 and len(text.strip()) > 2:
            return True

        # fallback: edge density
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        density = np.sum(edges) / (h * w)

        return 0.05 < density < 0.25

    except:
        return False
def infer_from_text(text):
    t = text.lower()

    return {
        "stamp": "stamp" in t or "seal" in t,
        "signature": "signature" in t or "signed" in t,
        "logo": any(x in t for x in ["company", "ltd", "inc", "s.p.a"])
    }


def detect_visual_elements(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return {"logo": False, "stamp": False, "signature": False, "regions": []}

    regions = get_candidate_regions(img)

    result = {
        "logo": False,
        "stamp": False,
        "signature": False,
        "regions": []
    }

    for (x, y, w, h) in regions:
        crop = img[y:y+h, x:x+w]

        label = "unknown"

        if is_blue_stamp(crop):
            result["stamp"] = True
            label = "stamp"
        elif is_signature_like(crop):
            result["signature"] = True
            label = "signature"
        elif is_logo_like(crop):
            result["logo"] = True
            label = "logo"

        result["regions"].append({
            "bbox": [int(x), int(y), int(w), int(h)],
            "label": label
        })

    return result


# =========================
# PDF EXTRACTION (SMART: TEXT + OCR)
# =========================
def enhance_for_ocr(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 🔥 contrast boost
        gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=30)

        # 🔥 sharpening
        kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
        sharp = cv2.filter2D(gray, -1, kernel)

        # 🔥 adaptive threshold
        thresh = cv2.adaptiveThreshold(
            sharp, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        return thresh
    except:
        return img


def multi_ocr(img):
    results = []

    # pass 1
    t1, c1 = safe_ocr_image(img)
    results.append((t1, c1))

    # pass 2 (resize)
    big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    t2, c2 = safe_ocr_image(big)
    results.append((t2, c2))

    # pass 3 (contrast only - NO threshold)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=15)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    t3, c3 = safe_ocr_image(gray)
    results.append((t3, c3))

    # 🔥 IMPORTANT: choose longest text (not highest confidence)
    best = max(results, key=lambda x: len(x[0]))

    return best


def safe_ocr_image(img):
    try:
        if img is None:
            return "", 0.0

        # 🔥 convert BGR → RGB (CRITICAL FIX)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        result = ocr.ocr(img_rgb)

        text = ""
        confs = []

        if result:
            for line in result:
                if line:
                    for word in line:
                        text += word[1][0] + " "
                        confs.append(word[1][1])

        avg = sum(confs)/len(confs) if confs else 0.0

        return text.strip(), avg

    except Exception as e:
        print("OCR ERROR:", e)
        return "", 0.0

def is_scanned_page(page):
    text = page.get_text().strip()
    return len(text) < 10


def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        print(f"Opened PDF: {file_path}, pages: {doc.page_count}")
    except:
        return "", "failed", 0.0, {}

    full_text = []
    total_conf = 0
    count = 0

    visual_data = {"logo": False, "stamp": False, "signature": False, "regions": []}

    for page in doc:

        # 🔥 detect scanned
        scanned = is_scanned_page(page)
        print(f"Page {page.number}: scanned={scanned}")

        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)

        try:
            #  HIGH DPI render (very important)
            pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))
            pix.save(tmp)

            img = cv2.imread(tmp)
            # debug_ocr_pipeline(img, page.number)

            #  OCR ALWAYS (even if digital)
            ocr_text, conf = multi_ocr(img)

            if scanned:
                # print(f"Page {page.number} is scanned. Using OCR text only. and file path: {tmp} and conf: {conf}")
                chosen_text = ocr_text
            else:
                text_layer = page.get_text()
                # print(f"Page {page.number}: text layer length={len(text_layer)}, OCR length={len(ocr_text)}",text_layer[:100], ocr_text[:100])
                # choose better
                chosen_text = ocr_text if len(ocr_text) > len(text_layer) else text_layer

            full_text.append(chosen_text)

            total_conf += conf
            count += 1

            # visual detection
            vis = detect_visual_elements(tmp)

            for k in ["logo", "stamp", "signature"]:
                visual_data[k] = visual_data[k] or vis[k]

            visual_data["regions"].extend(vis.get("regions", []))

        except Exception as e:
            print("PDF error:", e)
            full_text.append("")

        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except:
                pass

    doc.close()

    avg_conf = total_conf / count if count else 0.0

    return "\n".join(full_text), "mixed", avg_conf, visual_data


# =========================
# IMAGE EXTRACTION
# =========================
def extract_text_from_image(file_path):
    text, conf = safe_ocr(file_path)
    visual = detect_visual_elements(file_path)
    return text, {"visual": visual}, "ocr", conf


# =========================
# STRUCTURED FILES
# =========================
def extract_structured(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        structured = df.to_dict()
        text = df.astype(str).apply(lambda x: " ".join(x), axis=1).str.cat(sep="\n")

        return text, structured, "structured", 1.0
    except:
        return "", {}, "failed", 0.0


# =========================
# UNIVERSAL EXTRACTOR
# =========================
def extract_text_from_file(file_path):
    ext = file_path.lower()

    if ext.endswith(".pdf"):
        text, method, conf, visual = extract_text_from_pdf(file_path)
        return text, {"visual": visual}, method, conf

    elif ext.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_from_image(file_path)

    elif ext.endswith((".csv", ".xls", ".xlsx")):
        return extract_structured(file_path)

    elif ext.endswith(".txt"):
        with open(file_path, "r", errors="ignore") as f:
            return f.read(), {}, "text", 1.0

    return "", {}, "unknown", 0.0


# =========================
# FORENSIC SCORE
# =========================
def compute_forensic_score(doc):
    score = 0

    if doc.get("confidence", 0) > 0.6:
        score += 25

    if doc.get("clean_text"):
        score += 25

    visual = doc.get("visual_analysis", {})

    if visual.get("logo"):
        score += 10
    if visual.get("stamp"):
        score += 20
    if visual.get("signature"):
        score += 20

    return score


# =========================
# PROCESS DOCUMENTS
# =========================
def process_documents(files):
    documents = []

    for file in files:
        doc = {
            "file_path": file,
            "file_hash": generate_sha256(file),
            "status": "UNKNOWN",
            "failure_reason": None,
            "validation_flags": []
        }

        if not validate_file(file):
            doc["status"] = "FAILED"
            doc["failure_reason"] = "file_invalid"
            documents.append(doc)
            continue

        raw_text, structured, method, conf = extract_text_from_file(file)

        doc["extraction_method"] = method
        doc["confidence"] = conf if conf > 0 else (len(raw_text) / 1000)
        # doc["raw_text"] = (raw_text or "")

        visual = structured.get("visual", {})
        # doc["visual_analysis"] = visual

        if not raw_text.strip():
            doc["failure_reason"] = "empty_text"

        clean_text = normalize_text(raw_text)
        text_lower = clean_text.lower()
        text_flags = infer_from_text(clean_text)
        if "signature" in text_lower or "signed" in text_lower:
            visual["signature"] = True

        if "stamp" in text_lower or "official seal" in text_lower:
            visual["stamp"] = True

        if "logo" in text_lower or "company" in text_lower:
            visual["logo"] = True
        # visual["logo"] = visual.get("logo") or text_flags["logo"]
        # visual["stamp"] = visual.get("stamp") or text_flags["stamp"]
        # visual["signature"] = visual.get("signature") or text_flags["signature"]

        doc["visual_analysis"] = visual
        doc["clean_text"] = clean_text

        is_valid, flags = validate_text(clean_text)
        doc["validation_flags"] = flags
        doc["text_flags"] = text_flags

        score = compute_forensic_score(doc)
        doc["forensic_score"] = score

        if score >= 70:
            doc["status"] = "VERIFIED"
        elif score >= 40:
            doc["status"] = "PARTIAL"
        else:
            doc["status"] = "FAILED"

        documents.append(doc)

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
            if "__MACOSX" in name or name.startswith("."):
                continue
            files.append(os.path.join(root, name))
    return files


# =========================
# MAIN PIPELINE
# =========================
def process_case(zip_path):
    case_id = str(uuid.uuid4())[:8]

    extract_path = extract_zip(zip_path, case_id)
    files = get_all_files(extract_path)

    documents = process_documents(files)

    return {
        "case_id": case_id,
        "documents": documents,
        "total_files": len(files)
    }


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

    result = process_case(path)

    return JSONResponse({"success": True, "data": result}, status_code=200)