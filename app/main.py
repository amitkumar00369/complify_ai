import os
import zipfile
import uuid
import json
import re
import fitz
import pandas as pd
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from paddleocr import PaddleOCR

app = FastAPI()

BASE_DIR = "products_data"
OUTPUT_JSON = "cases_output.json"

os.makedirs(BASE_DIR, exist_ok=True)

# ✅ Fixed PaddleOCR initialization (remove unsupported parameters)
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Removed show_log parameter


# =========================
# CREATE CASE
# =========================
def create_case(zip_filename):
    return {
        "case_id": str(uuid.uuid4())[:8],
        "case_name": zip_filename,
        "product_type": "unknown",
        "documents": [],
        "product_data": {},
        "status": "PENDING"
    }


# =========================
# UNZIP
# =========================
def extract_zip(zip_path, case_id):
    extract_path = os.path.join(BASE_DIR, case_id)
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    return extract_path


# =========================
# GET FILES
# =========================
def get_all_files(folder_path):
    files = []

    for root, _, filenames in os.walk(folder_path):
        for file in filenames:
            full_path = os.path.join(root, file)

            if "__macosx" in full_path.lower():
                continue

            files.append(full_path)

    return files


# =========================
# SAFE OCR FUNCTION
# =========================
def safe_ocr(image_path):
    """Helper function for OCR with error handling"""
    try:
        result = ocr.ocr(image_path)
        if not result:
            return ""
        
        text = ""
        # Handle different OCR result formats
        if result and len(result) > 0:
            for line in result[0]:
                if len(line) >= 2:
                    text += line[1][0] + "\n"
        return text
    except Exception as e:
        print(f"OCR error for {image_path}: {e}")
        return ""


# =========================
# IMPROVED PDF TEXT EXTRACTOR
# =========================
def extract_text_from_pdf(file_path):
    """Extract ALL text from PDF including images via OCR"""
    full_text = []
    
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print(f"PDF open failed: {e}")
        return ""
    
    for page_num, page in enumerate(doc):
        page_text = []
        
        # Method 1: Extract embedded text layer
        try:
            text_layer = page.get_text("text")
            if text_layer and text_layer.strip():
                page_text.append(f"--- Page {page_num + 1} Text Layer ---\n{text_layer}")
        except Exception as e:
            print(f"Text extraction error page {page_num}: {e}")
        
        # Method 2: OCR on page images (for scanned PDFs or images)
        try:
            # Increase resolution for better OCR
            zoom = 2.0  # Higher resolution = better OCR but slower
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img_path = tmp_file.name
                pix.save(img_path)
            
            # Perform OCR
            ocr_text = safe_ocr(img_path)
            if ocr_text and ocr_text.strip():
                page_text.append(f"--- Page {page_num + 1} OCR Layer ---\n{ocr_text}")
            
            # Clean up temp file
            try:
                os.unlink(img_path)
            except:
                pass
            
        except Exception as e:
            print(f"OCR error page {page_num}: {e}")
        
        # Combine both layers
        if page_text:
            full_text.append("\n".join(page_text))
    
    doc.close()
    return "\n\n".join(full_text)


# =========================
# IMAGE TEXT EXTRACTOR
# =========================
def extract_text_from_image(file_path):
    """Extract text from single image"""
    try:
        result = ocr.ocr(file_path)
        if not result:
            return ""
        
        text = ""
        if result and len(result) > 0:
            for line in result[0]:
                if len(line) >= 2:
                    text += line[1][0] + "\n"
        return text.strip()
    except Exception as e:
        print(f"Image OCR error: {e}")
        return ""


# =========================
# UNIVERSAL TEXT EXTRACTOR
# =========================
def extract_text_from_file(file_path):
    ext = file_path.lower()
    
    try:
        # PDF with full OCR support
        if ext.endswith(".pdf"):
            return extract_text_from_pdf(file_path)
        
        # Image files
        elif ext.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
            return extract_text_from_image(file_path)
        
        # Excel files
        elif ext.endswith((".xlsx", ".xls")):
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
                return df.to_string()
            except:
                # Try with different engine for older .xls
                df = pd.read_excel(file_path)
                return df.to_string()
        
        # Text files
        elif ext.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        
        # CSV files
        elif ext.endswith(".csv"):
            df = pd.read_csv(file_path)
            return df.to_string()
        
        return ""
        
    except Exception as e:
        print(f"Extraction error for {file_path}: {e}")
        return ""


# =========================
# CLASSIFIER
# =========================
def classify_document(file_path, text=""):
    path = file_path.lower()
    text = text.lower()
    
    # Filename based classification
    if "msds" in path or "sds" in path:
        return "msds"
    if "technical" in path or "test report" in path:
        return "technical_report"
    if "risk" in path:
        return "risk"
    if "sdoc" in path or "declaration" in path:
        return "sdoc"
    if "pcoc" in path or "certificate" in path or "coa" in path:
        return "certificate"
    if "photo" in path or "label" in path or "image" in path:
        return "label"
    if "fa" in path or "audit" in path:
        return "factory_audit"
    if path.endswith((".xlsx", ".xls", ".csv")):
        return "product_list"
    
    # Content-based classification
    if "material safety data sheet" in text:
        return "msds"
    if "test report" in text or "test results" in text:
        return "technical_report"
    if "risk assessment" in text or "hazard analysis" in text:
        return "risk"
    if "declaration of conformity" in text or "ce declaration" in text:
        return "sdoc"
    if "certificate of analysis" in text:
        return "certificate"
    
    return "unknown"


# =========================
# PARSE TEXT
# =========================
def parse_text(text):
    text = text.lower()
    data = {}
    
    # Voltage: 100V, 220V, 230V, etc.
    voltage = re.findall(r'(\d{2,4})\s*v\b', text)
    if voltage:
        try:
            v = int(voltage[0])
            if 100 <= v <= 400:  # realistic voltage range
                data["voltage"] = v
        except:
            pass
    
    # Frequency: 50Hz, 60Hz
    freq = re.findall(r'(\d{2,3})\s*hz\b', text)
    if freq:
        try:
            f = int(freq[0])
            if f in (50, 60):
                data["frequency"] = f
        except:
            pass
    
    # Flammability
    if "flammable" in text or "highly flammable" in text:
        data["flammable"] = True
    
    # pH value
    ph = re.findall(r'ph[:\s]*(\d+\.?\d*)', text)
    if ph:
        try:
            val = float(ph[0])
            if 0 < val <= 14:
                data["ph"] = val
        except:
            pass
    
    # Additional extractions
    # Weight/Mass
    weight = re.findall(r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram)', text)
    if weight:
        try:
            data["weight_kg"] = float(weight[0])
        except:
            pass
    
    # Temperature
    temp = re.findall(r'(\d+(?:\.\d+)?)\s*°?\s*c', text)
    if temp:
        try:
            data["temperature_celsius"] = float(temp[0])
        except:
            pass
    
    return data


# =========================
# PROCESS DOCUMENTS
# =========================
def process_documents(file_list):
    documents = []
    
    for file in file_list:
        print(f"Processing: {file}")  # Progress indicator
        text = extract_text_from_file(file)
        
        # Skip if no text extracted
        if not text or not text.strip():
            continue
        
        doc_type = classify_document(file, text)
        structured = parse_text(text)
        
        documents.append({
            "file_path": file,
            "doc_type": doc_type,
            "textInsideThisFile": text[:5000],  # Increased limit
            "structured_data": structured
        })
    
    return documents


# =========================
# MERGE DATA
# =========================
def build_product_data(documents):
    product = {}
    
    # Priority documents (MSDS, Technical reports take precedence)
    for doc in documents:
        if doc["doc_type"] in ["msds", "technical_report", "sdoc"]:
            product.update(doc["structured_data"])
    
    # Secondary documents (fill missing data)
    for doc in documents:
        for key, value in doc["structured_data"].items():
            if key not in product:
                product[key] = value
    
    return product


# =========================
# DETECT TYPE
# =========================
def detect_product_type(product):
    if product.get("flammable") or product.get("ph"):
        return "chemical"
    if product.get("voltage") or product.get("frequency"):
        return "electrical"
    if product.get("weight_kg") or product.get("temperature_celsius"):
        return "physical_goods"
    return "unknown"


# =========================
# SAVE JSON
# =========================
def save_case(case):
    data = []
    
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    
    data.append(case)
    
    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# MAIN PIPELINE
# =========================
def process_case(zip_path):
    case = create_case(os.path.basename(zip_path))
    
    extract_path = extract_zip(zip_path, case["case_id"])
    files = get_all_files(extract_path)
    
    print(f"Found {len(files)} files to process")
    
    documents = process_documents(files)
    case["documents"] = documents
    
    product_data = build_product_data(documents)
    case["product_data"] = product_data
    
    case["product_type"] = detect_product_type(product_data)
    case["status"] = "PROCESSED"
    
    return case


# =========================
# ROUTE
# =========================
@app.post("/uploadCase")
async def upload_case(file: UploadFile = File(...)):
    try:
        # Validate file is zip
        if not file.filename.endswith('.zip'):
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Only ZIP files are accepted"
                },
                status_code=400
            )
        
        file_path = os.path.join(BASE_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        result = process_case(file_path)
        save_case(result)
        
        # Optional: Clean up zip file after processing
        # os.remove(file_path)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Case processed successfully",
                "data": result
            },
            status_code=200
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": str(e)
            },
            status_code=500
        )


# =========================
# HEALTH CHECK ENDPOINT
# =========================
@app.get("/health")
async def health_check():
    return {"status": "healthy"}