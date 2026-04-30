import os
import json
import re
import hashlib
import asyncio
import fitz  # PyMuPDF
import pandas as pd
from paddleocr import PaddleOCR

# -------------------------------
# CONFIG
# -------------------------------
DATA_STORE = "data_store.json"

ocr = PaddleOCR(use_angle_cls=True, lang='en')


# -------------------------------
# UTIL
# -------------------------------
def generate_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


async def save_json(data):
    if not os.path.exists(DATA_STORE):
        with open(DATA_STORE, "w") as f:
            json.dump([], f)

    with open(DATA_STORE, "r") as f:
        existing = json.load(f)

    existing.append(data)

    with open(DATA_STORE, "w") as f:
        json.dump(existing, f, indent=2)


# -------------------------------
# FILE TYPE
# -------------------------------
def detect_file_type(file_path):
    if file_path.endswith(".pdf"):
        return "pdf"
    elif file_path.endswith((".png", ".jpg", ".jpeg")):
        return "image"
    elif file_path.endswith((".xlsx", ".xls")):
        return "excel"
    else:
        return "unknown"


# -------------------------------
# PDF HANDLING
# -------------------------------
def is_scanned_pdf(path):
    doc = fitz.open(path)
    text = ""

    for page in doc:
        text += page.get_text()

    return len(text.strip()) < 50


async def extract_pdf_text(path):
    doc = fitz.open(path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text


async def extract_scanned_pdf(path):
    result = ocr.ocr(path)

    text = ""
    for line in result:
        for word in line:
            text += word[1][0] + " "

    return text


async def hybrid_pdf_extraction(path):
    doc = fitz.open(path)
    final_text = ""

    for page in doc:
        txt = page.get_text()

        if len(txt.strip()) > 20:
            final_text += txt
        else:
            # OCR fallback
            pix = page.get_pixmap()
            img_path = "temp_page.png"
            pix.save(img_path)
            ocr_text = await extract_scanned_pdf(img_path)
            final_text += ocr_text
            os.remove(img_path)

    return final_text


# -------------------------------
# IMAGE HANDLING
# -------------------------------
async def extract_image_text(path):
    return await extract_scanned_pdf(path)


# -------------------------------
# EXCEL HANDLING
# -------------------------------
async def extract_excel(path):
    df = pd.read_excel(path)
    return df.to_dict(orient="records")


# -------------------------------
# NORMALIZATION
# -------------------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\b(v|hz|volts)\b', '', text)
    return text.strip()


# -------------------------------
# CLAUSE DETECTION
# -------------------------------
def extract_candidate_clauses(text):
    sentences = re.split(r'[.\n]', text)

    candidates = []
    for s in sentences:
        s = s.strip()
        if len(s) > 25:
            candidates.append(s)

    return candidates


# -------------------------------
# LLaMA PARSER (DYNAMIC)
# -------------------------------
async def llama_parse(text):
    """
    Replace this with your actual LLaMA API call
    """
    # Mock dynamic parsing
    numbers = re.findall(r'\d+', text)

    result = {
        "field": None,
        "rule_type": None,
        "action": {},
        "raw_text": text
    }

    # dynamic guess (LLM-style fallback)
    if "between" in text:
        result["rule_type"] = "range"
        if len(numbers) >= 2:
            result["action"]["min"] = int(numbers[0])
            result["action"]["max"] = int(numbers[1])

    elif "must" in text:
        result["rule_type"] = "required"

    else:
        result["rule_type"] = "unknown"

    return result


# -------------------------------
# CLAUSE PARSER (HYBRID)
# -------------------------------
async def parse_clause(text):
    clause = {
        "raw_text": text,
        "source": "regex",
        "confidence": 0.6,
        "field": None,
        "rule_type": None,
        "action": {}
    }

    numbers = re.findall(r'\d+', text)

    if "between" in text and len(numbers) >= 2:
        clause["rule_type"] = "range"
        clause["action"] = {
            "min": int(numbers[0]),
            "max": int(numbers[1])
        }
        clause["confidence"] = 0.9

    else:
        # fallback to LLaMA
        llama_result = await llama_parse(text)
        clause.update(llama_result)
        clause["source"] = "llama"
        clause["confidence"] = 0.7

    return clause


# -------------------------------
# MAIN PIPELINE
# -------------------------------
async def process_file(file_path):

    # STEP 1: VALIDATION
    if not os.path.exists(file_path):
        raise Exception("File not found")

    file_hash = generate_hash(file_path)

    # STEP 2: TYPE
    file_type = detect_file_type(file_path)

    # STEP 3: EXTRACTION
    if file_type == "pdf":
        if is_scanned_pdf(file_path):
            text = await extract_scanned_pdf(file_path)
        else:
            text = await hybrid_pdf_extraction(file_path)

    elif file_type == "image":
        text = await extract_image_text(file_path)

    elif file_type == "excel":
        data = await extract_excel(file_path)
        text = json.dumps(data)

    else:
        return {"error": "Unsupported file"}

    # STEP 4: NORMALIZE
    text = normalize_text(text)

    # STEP 5: CLAUSE DETECT
    candidates = extract_candidate_clauses(text)

    # STEP 6: PARSE
    parsed_clauses = []
    for c in candidates:
        parsed = await parse_clause(c)
        parsed_clauses.append(parsed)

    # STEP 7: STORE
    document_record = {
        "file_path": file_path,
        "hash": file_hash,
        "type": file_type,
        "clauses": parsed_clauses
    }

    await save_json(document_record)

    return document_record


# -------------------------------
# RUN
# -------------------------------
