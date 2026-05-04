from ..core.extractor import extract_text
from ..core.common import sha256, normalize, validate, valid_file


def process_documents(files,hs_code=None):
    docs = []
   

    for file in files:
        # ext = file.lower()

        # =========================
        # FILE VALIDATION
        # =========================
        if not valid_file(file):
            continue

        # =========================
        # EXTRACT
        # =========================
        text, structured, method, conf = extract_text(file)
    

        #  safety fix (avoid crash)
        conf = float(conf) if isinstance(conf, (int, float)) else 0.0

        # =========================
        # CLEAN TEXT
        # =========================
        clean_text = normalize(text)
        # if ext.endswith((".png", ".jpg", ".jpeg")):
        #     hs_code = clean_text[:12]  # retry for PDFs
        # hs_code = 

        # =========================
        # VISUAL DATA
        # =========================
        visual = structured.get("visual", {}) if isinstance(structured, dict) else {}

        # =========================
        # VALIDATION
        # =========================
        is_valid = validate(clean_text)

        # =========================
        # BUILD RESPONSE
        # =========================
        doc = {
            "file": file,
            "hash": sha256(file),
            "hs_code": hs_code[:12],
            "method": method,
            "confidence": round(conf, 3),
            "valid": is_valid,
            "text_length": len(clean_text),
            "text": clean_text,
             "visual": visual

            # 🔥 important for your system
  
        }

        docs.append(doc)

    return docs