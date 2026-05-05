import re

def extract_clauses(text):
    if not text:
        return []

    text = text.lower()
    clauses = []

    # 🔹 Regulation
    if "machinery safety" in text:
        clauses.append({
            "type": "Regulation",
            "value": "Machinery Safety",
            "confidence": 0.9
        })

    # 🔹 Standard
    std = re.findall(r"(en\s*\d{4,5}[-–]?\d*)", text)
    if std:
        clauses.append({
            "type": "Standard",
            "value": std[0],
            "confidence": 0.95
        })

    # 🔹 Certificate
    if "certificate of conformity" in text or "coc" in text:
        clauses.append({
            "type": "Certification",
            "value": "COC",
            "confidence": 0.9
        })

    # 🔹 Test report
    if "test report" in text or "report number" in text:
        clauses.append({
            "type": "Test Report",
            "value": True,
            "confidence": 0.85
        })

    # 🔹 Product
    if "product name" in text:
        clauses.append({
            "type": "Product Identification",
            "confidence": 0.9
        })

    return clauses