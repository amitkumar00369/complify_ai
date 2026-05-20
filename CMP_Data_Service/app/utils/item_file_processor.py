from app.core_complaince.extractor import extract_text
from app.core_complaince.common import sha256, normalize, validate, valid_file
import json

import os
import uuid
import asyncio
import pandas as pd

from app.services.excel_service import extract_excel1
from app.services.clause import extract_clauses
from app.utils.text_cleaner import TextCleaner
from app.utils.trasnlate import TextTranslator
from app.utils.pcoc_file_extract_clause import pcocFIleClause
from app.services.product_item_servce import ProductService


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
    caseId,
    pcocClause
):
    # =========================
    # FILE VALIDATION
    # =========================
    is_file_valid = await asyncio.to_thread(valid_file, file)
    # print("yesss",is_file_valid, file)

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
    if hscode is not None:
        std_name = hscode.iloc[0]['Applicable Std.*']
    else:
        std_name = ""
        
    doc = {
        "caseId": caseId,
        "pcocData": pcocClause,
        "standard_name": std_name,
        "modelName": modelName,
        "product_info": os.path.basename(os.path.dirname(file)),
        "file_name": os.path.basename(file),
        "product_name": file_name,
        "folder_name": os.path.basename(os.path.dirname(os.path.dirname(file))),
        "sub_folder_name": os.path.basename(os.path.dirname(file)),
        "file_path": file,
        "hsCode_4": hsCode_4,
        "hash": file_hash,
        "hs_code": pcocClause.get("hs_code"),
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


async def process_documents(files, file_name=None):

    docs = []
    hscode = None
    modelName = []

    # =========================
    # EXCEL EXTRACTION
    # =========================
    clause = None
    for file in files:
        if file.lower().endswith((".pdf")):
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
            print(hscode.columns)

            modelName.append(
                hscode.iloc[0]['Model number*']
            )
    print("hs codesss", hscode)
    if hscode is not None:
         hsCode_4 = str(hscode.iloc[0]['HS Code'][:4])
    if hscode is None:
        modelName.append(clause["model"])
        hsCode_4 = clause["hs_code"]
        # print("model", modelName, hsCode_4)
        
    

    # =========================
    # LOAD JSON
    # =========================
   

    caseId = "ITEM" + uuid.uuid4().hex[:8].upper()

    # =========================
    # MATCH LOGIC
    # =========================
    print("clause",clause)
   

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
            caseId=caseId,
            pcocClause = clause
        )
        for file in files
    ]

    results = await asyncio.gather(*tasks)
    # print("keys",len(results))

    docs = [doc for doc in results if doc]
    # print("keys",len(docs))

    return docs



async def normalize_text(text):

        if text is None:
            return ""

        text = str(text).lower()

        text = text.replace("-", " ")
        text = text.replace("_", " ")

        text = " ".join(text.split())

        return text

    # =====================================================
    # MATCH PRODUCT
    # =====================================================

   
async def match_product(product_name, item):

        text = await normalize_text(
            json.dumps(item)
        )

        product_words = (
            await normalize_text(
                product_name
            )
        ).split()

        matched_words = 0

        for word in product_words:

            if word in text:
                matched_words += 1

        score = matched_words / len(product_words)

        return score >= 0.7
    
async def tr_data(hs_code,data):
    for item in data:
        matched = (
                    await match_product(
                        hs_code[:4],
                        item["text"]
                    )
                )

        if matched:
            
            return {
                "tr_id": item["id"],
                "tr_name": item["tr_name"]
            }
            
            
async def std_data(product_name,data):
    for item in data:
        matched = (
                    await match_product(
                        product_name,
                        item
                    )
                )

        if matched:
            
            return {
                "std_id": item["id"],
                "std_name": item["std_name"]
            }

                    

                   

        