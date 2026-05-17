import re

def extract_clauses(text):
    if not text:
        return []

    text = text.lower()
    clauses = []

    #  Regulation
    if "machinery safety" in text:
        clauses.append({
            "type": "Regulation",
            "value": "Machinery Safety",
            "confidence": 0.9
        })

    #  Standard
    std = re.findall(r"(en\s*\d{4,5}[-–]?\d*)", text)
    if std:
        clauses.append({
            "type": "Standard",
            "value": std[0],
            "confidence": 0.95
        })

    #  Certificate
    if "certificate of conformity" in text or "coc" in text:
        clauses.append({
            "type": "Certification",
            "value": "COC",
            "confidence": 0.9
        })

    #  Test report
    if "test report" in text or "report number" in text:
        clauses.append({
            "type": "Test Report",
            "value": True,
            "confidence": 0.85
        })

    #  Product
    if "product name" in text:
        clauses.append({
            "type": "Product Identification",
            "confidence": 0.9
        })

    return clauses

import re

def safe_extract(match):
    """Avoid crash if group not present"""
    if not match:
        return None
    try:
        return match.group(1).strip()
    except IndexError:
        return match.group(0).strip()


def extract_clauses_pipeline(text):
    clauses = {}

    # normalize once
    text_lower = text.lower()

    patterns = {
        "certificate_number": r'certificate number\s*([\w\-\/]+)',
        "issue_date": r'issue date\s*([\d\/\-.]+)',
        "expiry_date": r'expire date\s*([\d\/\-.]+)',
        "hs_code": r'hs code\s*(\d{4,12})',
        
        #  FIXED (handles special chars)
        "product_name": r'product name\s*([^\n|]+)',
        
        "country_of_origin": r'country of origin\s*([a-zA-Z\s]+)',
        
        #  FIXED (handles full company names)
        "manufacturer_name": r'manufacturer name\s*([^\n]+)',
        
        "standard": r'(saso\s*\d+\-?\d*)'
    }

    # =========================
    # REGEX EXTRACTION
    # =========================
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        clauses[key] = safe_extract(match)

    # =========================
    # LOGIC CLAUSES
    # =========================
    clauses["has_certificate"] = "certificate of conformity" in text_lower
    clauses["approved"] = "product approved" in text_lower

    # =========================
    # NORMALIZATION
    # =========================
    if clauses.get("country_of_origin"):
        clauses["country_of_origin"] = clauses["country_of_origin"].title()

    if clauses.get("product_name"):
        clauses["product_name"] = clauses["product_name"].strip(" /-|")

    # =========================
    # CONFIDENCE (basic)
    # =========================
    clauses["confidence"] = {
        k: 1.0 if v else 0.0 for k, v in clauses.items()
        if k not in ["confidence"]
    }

    return clauses