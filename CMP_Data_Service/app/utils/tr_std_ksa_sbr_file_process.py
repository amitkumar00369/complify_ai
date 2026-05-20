

import uuid
import os
import asyncio
import json

from app.utils.tr_requirement import GenericTechnicalRequirementExtractor,extract_toc
from app.utils.tr_clauses import LegalStructureParser
from app.utils.text_cleaner import TextCleaner
from app.services.image_service import extract_image
from app.services.pdf_service import extract_pdf, extract_excel
from app.services.hs_mapper import extract_hs_mapping
from app.services.std_clause import build_knowledge_objects
from app.core_complaince.common import normalize
from app.utils.arbic_char import SmartTranslator
from app.utils.extract_word import extract_word_file
from app.utils.extract_pdf_by_pages import extract_text_by_pages


# =========================================
# TECHNICAL REGULATION
# =========================================
async def process_tr(file_path):

    ext = file_path.lower()

    text, structured, method, conf = "", {}, "unknown", 0.0

    if ext.endswith(".pdf"):

        text, structured, method, conf = await asyncio.to_thread(
            extract_pdf,
            file_path
        )

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

    hs_mapping = await asyncio.to_thread(
        extract_hs_mapping,
        cleanText
    )

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
        "text_en": text_en,

        "metaJson": {
            "total_standards": hs_mapping.get(
                "total_standards",
                0
            ),

            "total_hs_codes": hs_mapping.get(
                "total_hs_codes",
                0
            ),

            "standards": hs_mapping.get(
                "standards",
                []
            ),

            "hs_codes": hs_mapping.get(
                "hs_codes",
                []
            )
        }
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
async def process_saber(file_path):

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

    clean_text = normalize(text)

    cleanText = TextCleaner.normalize_text(clean_text)

    clause = await asyncio.to_thread(
        build_knowledge_objects,
        cleanText
    )

    result = {
        "saber_id": "SABER" + str(uuid.uuid4())[:6],

        "saber_name": SmartTranslator.smart_translate(
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

        "metaText": cleanText,

        "extrated_method": method,

        "confidence": conf,

        "clause": clause
    }

    return result


# =========================================
# KSA SALEEM
# =========================================
async def process_ksa_saleem(file_path):

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

    clean_text = normalize(text)

    cleanText = TextCleaner.normalize_text(clean_text)

    clause = await asyncio.to_thread(
        build_knowledge_objects,
        cleanText
    )
    # print("breaked -scuccc",SmartTranslator.smart_translate(
    #         os.path.splitext(
    #             os.path.basename(file_path)
    #         )[0]
    #     ))

    result = {
        "ksa_id": "KSA" + str(uuid.uuid4())[:6],

        "ksa_name": SmartTranslator.smart_translate(
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

        "metaText": cleanText,

        "extrated_method": method,

        "confidence": conf,

        "clause": clause
    }

    return result

async def process_tr_req(file, start_page, end_page):
    try:

        ext = file.lower()
    

        text = ""
        structured = {}
        method = "unknown"
        conf = 0.0

        if ext.endswith(".pdf"):

            text = await asyncio.to_thread(
                extract_text_by_pages,
                file, start_page,end_page
            )

        # elif ext.endswith((".png", ".jpg", ".jpeg")):

        #     text, structured, method, conf = await asyncio.to_thread(
        #         extract_image,
        #         file
        #     )

        # elif ext.endswith((".doc", ".docx")):

        #     text, structured, method, conf = await asyncio.to_thread(
        #         extract_word_file,
        #         file
        #     )

        # elif ext.endswith(".txt"):

        #     text = file.decode("utf-8")

        clean_text = TextCleaner.normalize_text(text)
        # extractor_req = GenericTechnicalRequirementExtractor(clean_text)
        # # extractor = LegalStructureParser()
        # # clauses = extractor.parse(clean_text)

        # tr_requirement = extractor_req.extract()

    #     print(
    #         json.dumps(
    #             result,
    #             indent=2,
    #             ensure_ascii=False
    #         )
    # )
        
    # for key, value in result.items():

    #     if isinstance(value, list):

    #         print(f"{key}: {len(value)} extracted")

    #     elif isinstance(value, dict):

    #         print(f"{key}: {len(value.keys())} fields")

    #     else:

    #         print(f"{key}: extracted")

        result = {
            "req_id": "TR_Req" + str(uuid.uuid4())[:6],
      
            "text": clean_text,
         

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

            text, structured, method, conf = await asyncio.to_thread(
                extract_pdf,
                file
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
       

        result = {
            "toc_id": "TR_TOC" + str(uuid.uuid4())[:6],
            # "text": clean_text,
            "toc_index_data": extract_toc(clean_text)

        }

        return result

    except Exception as e:
        print(str(e))
        return None