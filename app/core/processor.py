import os
import uuid

from sympy import im

from app.services.excel_service import extract_excel1
from app.services.clause import extract_clauses

from ..core.extractor import extract_text
from ..core.common import sha256, normalize, validate, valid_file
import pandas as pd
def extract_codes(data):
    # print("Extracting HS codes from:", data)

    result = []

    for item in data:
        # Case 1: flat list of dicts
        if isinstance(item, dict) and 'hs_code' in item:
            result.append(item['hs_code'])

        # Case 2: nested list
        elif isinstance(item, list):
            for sub in item:
                if isinstance(sub, dict) and 'hs_code' in sub:
                    result.append(sub['hs_code'])

    return result
def process_documents(files,file_name=None):
    docs = []
    hscode = None
    modelName = []
    for file in files:
        if file.lower().endswith((".csv", ".xls", ".xlsx")):
            hscode = extract_excel1(file)
            modelName.append(hscode.iloc[0]['Model number*'])
    hsCode_4 = str(hscode.iloc[0]['HS Code'][:4] )
    df = pd.read_json("tr_results.json")
    #  if hsCode_4 in df['metaJson'].apply(lambda x: x.get('hs_mapping', {}).get('hs_codes', [])):
    caseId = "ITEM" + uuid.uuid4().hex[:8].upper()


# Extract HS codes
    df['hs_codes'] = df['metaJson'].apply(lambda x: x.get('hs_codes', []))

    # print("HS codes in TR results:", df['hs_codes'].tolist())

    # Clean HS codes
    df['hs_codes_clean'] = df['hs_codes'].apply(extract_codes)
    # print("Cleaned HS codes in TR results:", df['hs_codes_clean'].tolist())

    # Normalize input HS code (VERY IMPORTANT)
    # hsCode_4 = str(hsCode)[:4]

    # Match using prefix logic
    df['match'] = df['hs_codes_clean'].apply(
        lambda codes: any(code.startswith(hsCode_4) for code in codes)
    )

    # Get matched rows
    matched_rows = df[df['match']]

    print("Matched TRs for HS code", hsCode_4, ":\n", matched_rows['file_name'])
    TR_name =  matched_rows['titleInEng'].to_list()    # if None go for llm model to find the best match

    
    # print("Extracted HS codes from Excel files1:", hscode.iloc[0]['HS Code'] if not hscode.empty else "No HS codes found")
   

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
        clause = extract_clauses(clean_text)
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
            "caseId": caseId,
            "standard_name": hscode.iloc[0]['Applicable Std.*'],
            "modelName":modelName,
            "product_info" :os.path.basename(os.path.dirname(file)),
            "file_name": os.path.basename(file),
            "product_name":file_name,
            "folder_name": os.path.basename(os.path.dirname(os.path.dirname(file))),
            "sub_folder_name": os.path.basename(os.path.dirname(file)),
            "file_name": os.path.basename(file),
            "file_path": file,
            "TR_name": TR_name[0] if TR_name else None,
            "hsCode_4": hsCode_4,
            "hash": sha256(file),
            "hs_code": hscode.iloc[0]['HS Code'],
            "method": method,
            "confidence": round(conf, 3),
            "valid": is_valid,
            "text_length": len(clean_text),
            "text": clean_text,
             "visual": visual,
             "clause": clause

            # 🔥 important for your system
  
        }

        docs.append(doc)

    return docs