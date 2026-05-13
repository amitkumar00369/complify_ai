import os
import uuid
import asyncio
import pandas as pd

from app.services.excel_service import extract_excel1
from app.services.clause import extract_clauses
from app.utils.text_cleaner import TextCleaner
from app.utils.trasnlate import TextTranslator
from ..core.extractor import extract_text
from ..core.common import sha256, normalize, validate, valid_file
from app.utils.pcocFileExtractClause import pcocFIleClause

def extract_codes(data):
    result = []

    for item in data:
        if isinstance(item, dict) and 'hs_code' in item:
            result.append(item['hs_code'])

        elif isinstance(item, list):
            for sub in item:
                if isinstance(sub, dict) and 'hs_code' in sub:
                    result.append(sub['hs_code'])

    return result


async def process_single_file(
    file,
    file_name,
    hscode,
    modelName,
    hsCode_4,
    TR_name,
    caseId,
    pcocClause
):
    # =========================
    # FILE VALIDATION
    # =========================
    is_file_valid = await asyncio.to_thread(valid_file, file)

    if not is_file_valid:
        return None

    # =========================
    # EXTRACT TEXT
    # =========================
    text, structured, method, conf = await asyncio.to_thread(
        extract_text,
        file
    )

    conf = float(conf) if isinstance(conf, (int, float)) else 0.0

    # =========================
    # CLEAN TEXT
    # =========================
    clean_text = TextCleaner.normalize_text(text)
    translated_text =  TextTranslator.translate_to_english(clean_text)

    clause =extract_clauses(translated_text) 
    

    # =========================
    # VISUAL DATA
    # =========================
    visual = structured.get("visual", {}) if isinstance(structured, dict) else {}

    # =========================
    # VALIDATION
    # =========================
    is_valid = validate(clean_text)

    # =========================
    # HASH
    # =========================
    file_hash = await asyncio.to_thread(sha256, file)

    # =========================
    # BUILD RESPONSE
    # =========================
    doc = {
        "caseId": caseId,
        "pcocData": pcocClause,
        "standard_name": hscode.iloc[0]['Applicable Std.*'],
        "modelName": modelName,
        "product_info": os.path.basename(os.path.dirname(file)),
        "file_name": os.path.basename(file),
        "product_name": file_name,
        "folder_name": os.path.basename(os.path.dirname(os.path.dirname(file))),
        "sub_folder_name": os.path.basename(os.path.dirname(file)),
        "file_path": file,
        "TR_name": TR_name[0] if TR_name else None,
        "hsCode_4": hsCode_4,
        "hash": file_hash,
        "hs_code": hscode.iloc[0]['HS Code'],
        "method": os.path.splitext(file)[1].replace(".", "").lower(),
        "confidence": round(conf, 3),
        "valid": is_valid,
        "text_length": len(clean_text),
        "text": clean_text,
        "translated_text": translated_text,
        "visual": visual,
        "clause": clause
    }

    return doc


async def process_item_documents(files, file_name=None):

    docs = []
    hscode = None
    modelName = []

    # =========================
    # EXCEL EXTRACTION
    # =========================
    clause = None
    for file in files:
        if file.lower().endswith((".pdf")):
            print("file",file)
            if "pcoc" in os.path.basename(file).lower():
                text, structured, method, conf  = extract_text(file)
                clean_text = TextCleaner.normalize_text(text)
                translated_text =  TextTranslator.translate_to_english(clean_text)

                clause =pcocFIleClause.extractClause(translated_text) 
            else:
                continue
             
                 
                

        if file.lower().endswith((".csv", ".xls", ".xlsx")):

            hscode = await asyncio.to_thread(
                extract_excel1,
                file
            )

            modelName.append(
                hscode.iloc[0]['Model number*']
            )

    hsCode_4 = str(hscode.iloc[0]['HS Code'][:4])

    # =========================
    # LOAD JSON
    # =========================
    df = await asyncio.to_thread(
        pd.read_json,
        "tr_results.json"
    )

    caseId = "ITEM" + uuid.uuid4().hex[:8].upper()

    # =========================
    # MATCH LOGIC
    # =========================
    df['hs_codes'] = df['metaJson'].apply(
        lambda x: x.get('hs_codes', [])
    )

    df['hs_codes_clean'] = df['hs_codes'].apply(
        extract_codes
    )

    df['match'] = df['hs_codes_clean'].apply(
        lambda codes: any(
            code.startswith(hsCode_4)
            for code in codes
        )
    )

    matched_rows = df[df['match']]

    print(
        "Matched TRs for HS code",
        hsCode_4,
        ":\n",
        matched_rows['file_name']
    )

    TR_name = matched_rows['file_name'].to_list()

    # =========================
    # PROCESS FILES CONCURRENTLY
    # =========================
    tasks = [
        process_single_file(
            file=file,
            file_name=file_name,
            hscode=hscode,
            modelName=modelName,
            hsCode_4=hsCode_4,
            TR_name=TR_name,
            caseId=caseId,
            pcocClause = clause
        )
        for file in files
    ]

    results = await asyncio.gather(*tasks)

    docs = [doc for doc in results if doc]
    

    return docs