

import json
import json
import uuid
import os
import asyncio
# from app.services import clause
# from app.services.llama_service import  extract_section_compliance_data, extract_clauses,extract_requirements
from app.utils.ollam_service import StandardExtractor
from app.utils.constants import Technical_Key_Title
from app.utils.tr_reuirements_file import extract_clauses,extract_requirements,classify_section,extract_article_content,normalize_requirements,find_article_number
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
from app.utils.extract_pdf_by_pages import extract_text_by_pages,countDoc
from app.utils.tr_toc_extracted import extract_toc ,refine_toc
from app.utils.tr_requirements_new import extract_regulation_structures
# from app.utils.tr_std_codes import extract_standards

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
    trace_id = str(uuid.uuid4())[:8]

    print(
        f"[{trace_id}] "
        f"Processing saber file: "
        f"{file_path}"
    )

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
        fullText = ""
        structured = {}
        method = "unknown"
        conf = 0.0
        totalPagesOfDoc = 0

        if ext.endswith(".pdf"):
            totalPagesOfDoc = await asyncio.to_thread(
                countDoc,file
            )

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
        # print("totalPagesOfDoc",totalPagesOfDoc , clean_text, totalPagesOfDoc)
        table_of_contents = extract_toc(clean_text)
        table_of_contents= refine_toc(table_of_contents,totalPagesOfDoc)
        # print("extracted toc", table_of_contents)
        toc_data = []
        allText = ""
        for idx, item in enumerate(table_of_contents):
            title_text = await asyncio.to_thread(
                extract_text_by_pages,
                file,item["start_page"],item["end_page"]
            )
            data = {
                "section": item["section"],
                "start_page": item["start_page"],
                "end_page": item["end_page"],
                "content": TextCleaner.normalize_text(title_text) or ""
            }
            toc_data.append(data)
            allText += TextCleaner.normalize_text(title_text)
        # print(clean_text)
        all_section_results = []
        all_title = []
        hs_codes = []
        std_codes = []
  
        

        for item in toc_data:
            all_title.append( item["section"])
     
            if  item["section"] in Technical_Key_Title.get("hs_code",[]):
                # print(item["content"])
                hs_codes = extract_product_hs_codes(item["content"])
            if  item["section"] in Technical_Key_Title.get("standard",[]):
                # print(item["content"])
                std_codes = extract_standards(item["content"])
                # stdData = StandardExtractor.extract_standards(item["content"])
                # print()
                # print(stdData)
            try:
                classification = classify_section(
                    item["section"]
                )
                

                if not classification["should_process"]:
                    continue
                if classification["type"]=="conformity_assessment" and "article" in item["section"].lower():
                    article_number = find_article_number( item["section"])
                    # print("classification",classification,item["section"])
                    article= extract_article_content(article_number,item["content"])
                    # print(f"article_number {article_number}",article)
                    clauses = extract_clauses(article)
                    # print("cvlvkvk",clauses)
                    for clause in clauses:
                        # print(clause["clause"])
                        # print(clause["content"])
                        requirements = extract_requirements(
                        clause["clause"],
                        clause["content"]
                    )

                        if requirements:
                            all_section_results.extend(
                                requirements
                            )

                        
                   
                    
                

                    # result = extract_section_compliance_data(
                    #     classification["type"],
                    #     item["section"],
                    #     item["content"]
                    # )
               
            except Exception as e:
                print(
                    f"Error processing section: {item['section']}",
                    str(e)
                )
                continue

      
   

        result = {
            "toc_id": "TR_TOC" + str(uuid.uuid4())[:6],
            "text": allText,
            "toc_index_data": toc_data or [],
            "compliance_data": normalize_requirements(all_section_results) or [],
            "hs_codes": hs_codes or [],
            "std_codes": std_codes or [],
            "table_of_contents":table_of_contents

        }

        return result

    except Exception as e:
        print(str(e))
        return None