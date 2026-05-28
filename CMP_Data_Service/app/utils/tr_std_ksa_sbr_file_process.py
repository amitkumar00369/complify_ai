

import uuid
import os
import asyncio

from app.utils.tr_hs_code import extract_product_hs_codes
from app.utils.tr_header_data import extract_tr_cover_metadata
from app.utils.cmt_extract import extract_ksa_compliance_data
from app.utils.tr_std_codes import extract_standards
from app.utils.text_cleaner import TextCleaner
from app.services.image_service import extract_image
from app.services.pdf_service import extract_pdf, extract_excel, extract_saber_excel
from app.services.hs_mapper import extract_hs_mapping
from app.services.std_clause import build_knowledge_objects
from app.core_complaince.common import normalize
from app.utils.arbic_char import SmartTranslator
from app.utils.extract_word import extract_word_file
from app.utils.extract_pdf_by_pages import extract_text_by_pages
from app.utils.tr_toc_extracted import extract_toc
from app.utils.tr_requirements_new import extract_regulation_structures

from app.utils.tr_clause import transform_regulation_structure


# =========================================
# TECHNICAL REGULATION
# =========================================
async def process_tr(file_path):

    ext = file_path.lower()

    text, structured, method, conf = "", {}, "unknown", 0.0
    text1 = ""

    if ext.endswith(".pdf"):

        text, structured, method, conf = await asyncio.to_thread(
            extract_pdf,
            file_path
        )
        text1 = await asyncio.to_thread(
            extract_text_by_pages,
            file_path,1,1
        )
        # print("teeeext111", text1)

    elif ext.endswith((".png", ".jpg", ".jpeg")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_image,
            file_path
        )
    elif ext.endswith((".doc", ".docx")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_word_file,
            file_path
        )

    cleanText = TextCleaner.normalize_text(text)
    # text_en = SmartTranslator.translate_text_chunks(cleanText)

    # hs_mapping = await asyncio.to_thread(
    #     extract_hs_mapping,
    #     cleanText
    # )

    result = {
        "tr_id": "TR" + str(uuid.uuid4())[:6],

        "tr_name": SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        ),

        "file_name": os.path.basename(file_path),

        "titleInEng": SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        ),

        "metaText": cleanText,
        # "text_en": text_en,

        "metaJson":extract_tr_cover_metadata(text1)
    }

    return result


# =========================================
# STANDARD
# =========================================
async def process_std(file_path):

    ext = file_path.lower()

    text, structured, method, conf = "", {}, "unknown", 0.0

    if ext.endswith(".pdf"):

        text, structured, method, conf = await asyncio.to_thread(
            extract_pdf,
            file_path
        )
    elif ext.endswith((".doc", ".docx")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_word_file,
            file_path
        )

    elif ext.endswith((".png", ".jpg", ".jpeg")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_image,
            file_path
        )

    clean_text = normalize(text)

    cleanText = TextCleaner.normalize_text(clean_text)

    clause = await asyncio.to_thread(
        build_knowledge_objects,
        cleanText
    )

    result = {
        "std_id": "STD" + str(uuid.uuid4())[:6],

        "std_name": SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        ),

        "folder_name": os.path.basename(
            os.path.dirname(
                os.path.dirname(file_path)
            )
        ),

        "sub_folder_name": os.path.basename(
            os.path.dirname(file_path)
        ),

        "file_name": os.path.basename(file_path),

        "text_length": len(text),

        "metaText": clean_text,

        "extrated_method": method,

        "confidence": conf,

        "clause": clause
    }

    return result


# =========================================
# SABER
# =========================================
async def process_saber(file_path,saber_name):
    print("Processing saber file:", file_path, "with name:", saber_name)

    ext = file_path.lower()

    text, structured, method, conf = "", {}, "unknown", 0.0

    if ext.endswith(".pdf"):

        text, structured, method, conf = await asyncio.to_thread(
            extract_pdf,
            file_path
        )

    elif ext.endswith((".excel", ".csv", ".xlsx")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_excel,
            file_path
        )
    elif ext.endswith((".doc", ".docx")):
        print("files..............",file_path)

        text, structured, method, conf = await asyncio.to_thread(
            extract_word_file,
            file_path
        )
    elif ext.endswith((".png", ".jpg", ".jpeg")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_image,
            file_path
        )
    print("type of", type(text))
    clean_text = "Empty",
    cleanText = " Empty"
    clause = {}
    if not isinstance(text,list):
        clean_text = normalize(text)

        cleanText = TextCleaner.normalize_text(clean_text)

        clause = await asyncio.to_thread(
            build_knowledge_objects,
            cleanText
        )
    if isinstance(text,list):
        clause = text
        # print("clssss", clause)
            

    result = {
        "saber_id": "SABER" + str(uuid.uuid4())[:6],

        "saber_name": SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        ),
        "saber_name1": saber_name,
        "type": "saber",

        "folder_name": os.path.basename(
            os.path.dirname(
                os.path.dirname(file_path)
            )
        ),

        "sub_folder_name": os.path.basename(
            os.path.dirname(file_path)
        ),

        "file_name": os.path.basename(file_path),

        "text_length": len(text),

        "metaText": cleanText,

        "extrated_method": method,

        "confidence": conf,

        "clause": clause
    }

    return result


# =========================================
# KSA SALEEM
# =========================================
async def process_ksa_saleem(file_path,saber_name):

    ext = file_path.lower()

    text, structured, method, conf = "", {}, "unknown", 0.0

    if ext.endswith(".pdf"):

        text, structured, method, conf = await asyncio.to_thread(
            extract_pdf,
            file_path
        )

    elif ext.endswith((".excel", ".csv", ".xlsx")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_excel,
            file_path
        )

    elif ext.endswith((".png", ".jpg", ".jpeg")):

        text, structured, method, conf = await asyncio.to_thread(
            extract_image,
            file_path
        )

    print("type of", type(text))
    clean_text = "Empty",
    cleanText = " Empty"
    clause = {}
    if not isinstance(text,list):
        clean_text = normalize(text)

        cleanText = TextCleaner.normalize_text(clean_text)

        clause = await asyncio.to_thread(
            build_knowledge_objects,
            cleanText
        )
    if isinstance(text,list):
        clause = text
    if  saber_name.lower()=="cst":
        clause = extract_ksa_compliance_data(cleanText)
    # print("breaked -scuccc",SmartTranslator.smart_translate(
    #         os.path.splitext(
    #             os.path.basename(file_path)
    #         )[0]
    #     ))

    result = {
        "ksa_id": "KSA" + str(uuid.uuid4())[:6],
        "type": "KSA_SALEEM",

        "ksa_name": SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        ),
        "ksa_name1": saber_name,

        "folder_name": os.path.basename(
            os.path.dirname(
                os.path.dirname(file_path)
            )
        ),

        "sub_folder_name": os.path.basename(
            os.path.dirname(file_path)
        ),

        "file_name": os.path.basename(file_path),

        "text_length": len(text),

        "metaText": cleanText,

        "extrated_method": method,

        "confidence": conf,

        "clause": clause
    }
    # print("ress", result)

    return result


async def process_tr_req(file, start_page, end_page,text_scope):
    try:
        print("pagessss", start_page, end_page)

        ext = file.lower()
    

        text = ""

        if ext.endswith(".pdf"):

            text = await asyncio.to_thread(
                extract_text_by_pages,
                file, start_page,end_page
            )
        # print(text)
        

      

        clean_text = TextCleaner.normalize_text(text)
        # print(clean_text)
        
        # tr_req, req_text,tr_code = extract_regulation_structure(clean_text)
        data = extract_regulation_structures(clean_text,text_scope)
        # print(data)
        cluases = transform_regulation_structure(data.get("tr_requirement"))
      
        result = {
            "req_id": "TR_Req" + str(uuid.uuid4())[:6],
            "tr_code": data.get("tr_code"),
            "clean_text": clean_text,
            "text": data.get("req_raw_data"),
            "req": data.get("tr_requirement"),
            "cluases": cluases
         

        }

        return result

    except Exception as e:
        print(str(e))
        return None
    

async def process_tr_hs(file, start_page, end_page,text_scope):
    try:
        if start_page>end_page:
            end_page= start_page+3
        print("pagessss", start_page, end_page)
         

        ext = file.lower()
    

        text = ""

        if ext.endswith(".pdf"):

            text = await asyncio.to_thread(
                extract_text_by_pages,
                file, start_page,end_page
            )
        # print(text)
      
        

      

        clean_text = TextCleaner.normalize_text(text)
        # print(clean_text)
        data = extract_product_hs_codes(clean_text,text_scope)
        
        # tr_req, req_text,tr_code = extract_regulation_structure(clean_text)

      
        result = {
            "req_id": "TR_Req" + str(uuid.uuid4())[:6],
        
            # "clean_text": clean_text,
            "data": data
          
         

        }

        return result

    except Exception as e:
        print(str(e))
        return None
    

async def process_tr_std(file, start_page, end_page,text_scope):
    try:
        print("pagessss", start_page, end_page)

        ext = file.lower()
    

        text = ""

        if ext.endswith(".pdf"):

            text = await asyncio.to_thread(
                extract_text_by_pages,
                file, start_page,end_page
            )
        # print(text)
        

      

        clean_text = TextCleaner.normalize_text(text)
        data = extract_standards(text,text_scope)
        # print(clean_text)
        # data = extract_product_hs_codes(clean_text,text_scope)
        
        # tr_req, req_text,tr_code = extract_regulation_structure(clean_text)

      
        result = {
            "req_id": "TR_Req" + str(uuid.uuid4())[:6],
            "data": data
        }

        return result

    except Exception as e:
        print(str(e))
        return None
    
    

async def process_tr_toc(filename,file):
    try:

        ext = file.lower()
    

        text = ""
        structured = {}
        method = "unknown"
        conf = 0.0

        if ext.endswith(".pdf"):

            text = await asyncio.to_thread(
                extract_text_by_pages,
                file,2,3
            )

        elif ext.endswith((".png", ".jpg", ".jpeg")):

            text, structured, method, conf = await asyncio.to_thread(
                extract_image,
                file
            )

        elif ext.endswith((".doc", ".docx")):

            text, structured, method, conf = await asyncio.to_thread(
                extract_word_file,
                file
            )

        elif ext.endswith(".txt"):

            text = file.decode("utf-8")

        clean_text = TextCleaner.normalize_text(text)
        # print(clean_text)
       

        result = {
            "toc_id": "TR_TOC" + str(uuid.uuid4())[:6],
            # "text": clean_text,
            "toc_index_data": extract_toc(clean_text)

        }

        return result

    except Exception as e:
        print(str(e))
        return None