from app.utils.data_processing_for_schema import ResponseBuilder

import os
import json
import uuid
import asyncio
import aiofiles
import zipfile

from fastapi import UploadFile, File, Depends
from fastapi.responses import JSONResponse

from app.utils.tr_std_ksa_sbr_file_process import process_tr, process_tr_hs, process_tr_std, process_tr_toc,process_tr_req

from app.utils.zip_file import (
    BASE_DIR,
    extract_zip,
    get_files,cleanup_file,cleanup_folder
)
from starlette import status
from app.utils.arbic_char import SmartTranslator

from app.services.tr_regulations_requirements_service import (
    TR_REQUIREMENTS_Service,
    get_tr_requirements_service
)
from app.services.TR_toc import (
    TR_TOC_Service,
    get_tr_toc_service
)
from app.services.technical_regulation_service import (
    TechnicalRegulationService,
    get_technical_regulation_service
)

# ==========================================
# UPLOAD TR
# ==========================================
async def upload_tr(
    file: UploadFile = File(...),
    tr_service:  TechnicalRegulationService =  Depends(
        get_technical_regulation_service
    )
    
):
    try:
        path = None
        folder = None
        

        if not file.filename.endswith(
                    (".zip", ".pdf")
                ):

                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "message": "ZIP and PDF only"
                        }
                    )


        
        unique_name = (
                f"{uuid.uuid4()}_{file.filename}"
            )

        print(
            f"Received file: {file.filename}"
        )

        path = os.path.join(
            BASE_DIR,
            unique_name
        )

        # =========================
        # SAVE FILE (STREAMING) With Validation
        # =========================
        MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000 MB
        CHUNK_SIZE = 1024 * 1024           # 1 MB


        # =========================
        # SAVE FILE (STREAMING)
        # WITH FILE SIZE VALIDATION
        # =========================
        current_size = 0

        async with aiofiles.open(
            path,
            "wb"
        ) as out_file:

            while chunk := await file.read(CHUNK_SIZE):

                current_size += len(chunk)

                # =========================
                # FILE SIZE VALIDATION
                # =========================
                if current_size > MAX_FILE_SIZE:

                    # delete partial uploaded file
                    await out_file.close()

                    if os.path.exists(path):
                        os.remove(path)

                    return JSONResponse(
                        {
                            "error": (
                                "File too large. "
                                "Maximum allowed size is 500 MB"
                            )
                        },
                        status_code=400
                    )

                await out_file.write(chunk)


        # ==========================================
        # EXTRACT ZIP
        # ==========================================
        case_id = str(uuid.uuid4())[:8]

        is_zip = file.filename.lower().endswith(
                ".zip"
            )

            # =========================
            # EXTRACT ZIP
            # =========================
        if is_zip:

            try:

                folder = await asyncio.to_thread(
                    extract_zip,
                    path,
                    case_id
                )

            except zipfile.BadZipFile:

                return JSONResponse(
                    {
                        "error": "Invalid ZIP file"
                    },
                    status_code=400
                )

            files = await asyncio.to_thread(
                get_files,
                folder
            )

        else:

            files = [path]

        # ==========================================
        # PROCESS FILES CONCURRENTLY
        # ==========================================
        tasks = [
            process_tr(f_path)
            for f_path in files
        ]
        

        processed_results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )
        print("processed result",len(processed_results))
        # return {
        #     "data": processed_results
        # }
        docs = await ResponseBuilder.buildResponseOfTechnicalRegulation(processed_results)
        
        tr_data =await tr_service.create_tr_in_bulk(docs)
        

        # ==========================================
        # HANDLE RESULTS
        # ==========================================
    

        return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "TR created successfully",
                    "data": tr_data
                }
            )

    except Exception as e:

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": str(e)
            }
        )
    finally:

        # =========================
        # CLEANUP UPLOADED FILE
        # =========================
        if path:

            await asyncio.to_thread(
                cleanup_file,
                path
            )

        # =========================
        # CLEANUP EXTRACTED FOLDER
        # =========================
        if folder:

            await asyncio.to_thread(
                cleanup_folder,
                folder
            )



# ==========================================
# GET TR
# ==========================================
async def get_tr():

    json_path = "tr_results.json"

    if os.path.exists(json_path):

        print(
            f"Loading TR results "
            f"from {json_path}..."
        )

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as f:

            print(
                f"size of TR results file: "
                f"{os.path.getsize(json_path)} bytes"
            )

            try:

                data = json.load(f)

            except Exception as e:

                print(
                    "JSON ERROR:",
                    str(e)
                )

                # DEBUG CORRUPTED JSON
                f.seek(0)

                print(f.read()[:500])

                data = []

    else:

        data = []

    return {
        "total_items": len(data),
        "data": data
    }
    
async def get_tr():

    json_path = "tr_results.json"

    if os.path.exists(json_path):

        print(
            f"Loading TR results "
            f"from {json_path}..."
        )

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as f:

            print(
                f"size of TR results file: "
                f"{os.path.getsize(json_path)} bytes"
            )

            try:

                data = json.load(f)

            except Exception as e:

                print(
                    "JSON ERROR:",
                    str(e)
                )

                # DEBUG CORRUPTED JSON
                f.seek(0)

                print(f.read()[:500])

                data = []

    else:

        data = []

    return {
        "total_items": len(data),
        "data": data
    }
    



async def findTrToc(file: UploadFile = File(...), TR_Toc_service: TR_TOC_Service=Depends(get_tr_toc_service), tr_service:  TechnicalRegulationService =  Depends(
        get_technical_regulation_service
    ) ):
        try:
            path = None
            folder = None
            filename = file.filename
            # print("file_name", filename)
            tr_name = SmartTranslator.smart_translate(
              os.path.splitext(filename)[0])
            # print("tr_name", tr_name)
          
            tr_data = await tr_service.find_by_name(tr_name)
            if tr_data is None:
                return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                                "message": "Technical regulations not exist",
                                "status": 400
                            }
                )
            tr_toc_data = await TR_Toc_service.find_by_name(tr_name)
            if tr_toc_data is not None:
                 return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                                "message": f"Toc already exist for this file {tr_name} ",
                                "status": 400
                            }
                )
                
            
          
            

            if not file.filename.endswith(
                        (".zip", ".pdf",".docx",".txt")
                    ):

                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "message": "ZIP and PDF only"
                            }
                        )


            
            unique_name = (
                    f"{uuid.uuid4()}_{file.filename}"
                )

            print(
                f"Received file: {file.filename}"
            )

            path = os.path.join(
                BASE_DIR,
                unique_name
            )

            # =========================
            # SAVE FILE (STREAMING) With Validation
            # =========================
            MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000 MB
            CHUNK_SIZE = 1024 * 1024           # 1 MB


            # =========================
            # SAVE FILE (STREAMING)
            # WITH FILE SIZE VALIDATION
            # =========================
            current_size = 0

            async with aiofiles.open(
                path,
                "wb"
            ) as out_file:

                while chunk := await file.read(CHUNK_SIZE):

                    current_size += len(chunk)

                    # =========================
                    # FILE SIZE VALIDATION
                    # =========================
                    if current_size > MAX_FILE_SIZE:

                        # delete partial uploaded file
                        await out_file.close()

                        if os.path.exists(path):
                            os.remove(path)

                        return JSONResponse(
                            {
                                "error": (
                                    "File too large. "
                                    "Maximum allowed size is 500 MB"
                                )
                            },
                            status_code=400
                        )

                    await out_file.write(chunk)


            # ==========================================
            # EXTRACT ZIP
            # ==========================================
            case_id = str(uuid.uuid4())[:8]

            is_zip = file.filename.lower().endswith(
                    ".zip"
                )

                # =========================
                # EXTRACT ZIP
                # =========================
            if is_zip:

                try:

                    folder = await asyncio.to_thread(
                        extract_zip,
                        path,
                        case_id
                    )

                except zipfile.BadZipFile:

                    return JSONResponse(
                        {
                            "error": "Invalid ZIP file"
                        },
                        status_code=400
                    )

                files = await asyncio.to_thread(
                    get_files,
                    folder
                )

            else:

                files = [path]

            # ==========================================
            # PROCESS FILES CONCURRENTLY
            # ==========================================
            tasks = [
                process_tr_toc(filename,f_path)
                for f_path in files
            ]
            

            processed_results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            print("processed result",len(processed_results))
            if not processed_results:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "File not processes created successfully",
                        "data": processed_results
                    }
                )
            toc_data = processed_results[0]
                
            payload = {
                "tr_toc_id":  toc_data.get("toc_id"),
                "toc_index_data": toc_data.get("toc_index_data"),
                "tr_id": tr_data.get("id"),
                "tr_name": tr_data.get("tr_name")
            }
            # print("payload", payload)
            tr_toc_data = await TR_Toc_service.create_tr_toc(payload)
            
            
            # return {
            #     "data": processed_results
            # }
        
            

            # ==========================================
            # HANDLE RESULTS
            # ==========================================
        

            return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "message": "TOC created successfully",
                        "data": tr_toc_data
                    }
                )

        except Exception as e:

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": str(e)
                }
            )
        finally:

            # =========================
            # CLEANUP UPLOADED FILE
            # =========================
            if path:

                await asyncio.to_thread(
                    cleanup_file,
                    path
                )

            # =========================
            # CLEANUP EXTRACTED FOLDER
            # =========================
            if folder:

                await asyncio.to_thread(
                    cleanup_folder,
                    folder
                )






async def FindTrRequirement(file: UploadFile = File(...), TR_Req_service: TR_REQUIREMENTS_Service=Depends(get_tr_requirements_service),TR_Toc_service: TR_TOC_Service=Depends(get_tr_toc_service), tr_service:  TechnicalRegulationService =  Depends(
        get_technical_regulation_service
    )):
        try:
            path = None
            folder = None
            filename = file.filename
            # print("file_name", filename)
            tr_name = SmartTranslator.smart_translate(
              os.path.splitext(filename)[0])
            # print("tr_name", tr_name)
            tr_data = await tr_service.find_by_name(tr_name)
            if tr_data is None:
                return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                                "message": "Technical regulations not exist",
                                "status": 400
                            }
                )
            tr_req_data = await TR_Req_service.find_by_name(tr_name)
            print("hii",tr_req_data)
            if tr_req_data is not None:
                return JSONResponse(
                        status_code=400,
                        content={
                                "message": f"TR - Req already exist for this file {tr_name} ",
                                "status": 400
                            }
                )
                
            tr_toc_data = await TR_Toc_service.find_by_name(tr_name)
            if tr_toc_data is None:
                 return JSONResponse(
                        status_code=404,
                        content={
                                "message": f"Toc not exist for this file {tr_name} ",
                                "status": 404
                            }
                )
            start_page = None
            end_page = None
            for item in tr_toc_data.get("toc_index_data",[]):
                if item.get("section").lower()=="Obligations of Supplier".lower() or item.get("section").lower()=="Supplier s Obligations".lower() or  item.get("section").lower()=="Obligations of the Supplier".lower():
                    start_page = item.get("start_page")
                    end_page = item.get("end_page")
            print("start_page", start_page, end_page)
                    
                
            
          
            
            

            if not file.filename.endswith(
                        (".zip", ".pdf",".docx",".txt")
                    ):

                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "message": "ZIP and PDF only"
                            }
                        )


            
            unique_name = (
                    f"{uuid.uuid4()}_{file.filename}"
                )

            print(
                f"Received file: {file.filename}"
            )

            path = os.path.join(
                BASE_DIR,
                unique_name
            )

            # =========================
            # SAVE FILE (STREAMING) With Validation
            # =========================
            MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000 MB
            CHUNK_SIZE = 1024 * 1024           # 1 MB


            # =========================
            # SAVE FILE (STREAMING)
            # WITH FILE SIZE VALIDATION
            # =========================
            current_size = 0

            async with aiofiles.open(
                path,
                "wb"
            ) as out_file:

                while chunk := await file.read(CHUNK_SIZE):

                    current_size += len(chunk)

                    # =========================
                    # FILE SIZE VALIDATION
                    # =========================
                    if current_size > MAX_FILE_SIZE:

                        # delete partial uploaded file
                        await out_file.close()

                        if os.path.exists(path):
                            os.remove(path)

                        return JSONResponse(
                            {
                                "error": (
                                    "File too large. "
                                    "Maximum allowed size is 500 MB"
                                )
                            },
                            status_code=400
                        )

                    await out_file.write(chunk)


            # ==========================================
            # EXTRACT ZIP
            # ==========================================
            case_id = str(uuid.uuid4())[:8]

            is_zip = file.filename.lower().endswith(
                    ".zip"
                )

                # =========================
                # EXTRACT ZIP
                # =========================
            if is_zip:

                try:

                    folder = await asyncio.to_thread(
                        extract_zip,
                        path,
                        case_id
                    )

                except zipfile.BadZipFile:

                    return JSONResponse(
                        {
                            "error": "Invalid ZIP file"
                        },
                        status_code=400
                    )

                files = await asyncio.to_thread(
                    get_files,
                    folder
                )

            else:

                files = [path]

            # ==========================================
            # PROCESS FILES CONCURRENTLY
            # ==========================================
            tasks = [
                process_tr_req(f_path, start_page, end_page)
                for f_path in files
            ]
            

            processed_results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            print("processed result",len(processed_results))
            if not processed_results:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "File not processes created successfully",
                        "data": processed_results
                    }
                )
            req_data = processed_results[0]
                
            payload = {
                "req_id":  req_data.get("req_id"),
                "tr_code": req_data.get("tr_code"),
                "req_raw_data": req_data.get("text"),
                "tr_requirement": req_data.get("req"),
                "tr_req_clauses": req_data.get("cluases"),
                # "data": req_data.get("data"),
                
                "tr_toc_id": tr_toc_data.get("id"),
                "tr_id": tr_data.get("id"),
                "tr_name": tr_data.get("tr_name")
            }
            # print("payload", payload)
            # tr_req_data = await TR_REQUIREMENTS_Service.create_tr_toc(payload)
        
            

            # ==========================================
            # HANDLE RESULTS
            # ==========================================
        

            return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "message": "TR_Req created successfully",
                        "data": payload
                    }
                )

        except Exception as e:

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": str(e)
                }
            )
        finally:

            # =========================
            # CLEANUP UPLOADED FILE
            # =========================
            if path:

                await asyncio.to_thread(
                    cleanup_file,
                    path
                )

            # =========================
            # CLEANUP EXTRACTED FOLDER
            # =========================
            if folder:

                await asyncio.to_thread(
                    cleanup_folder,
                    folder
                )
                
                

async def findTrHSCode(file: UploadFile = File(...), TR_Req_service: TR_REQUIREMENTS_Service=Depends(get_tr_requirements_service),TR_Toc_service: TR_TOC_Service=Depends(get_tr_toc_service), tr_service:  TechnicalRegulationService =  Depends(
        get_technical_regulation_service
    )):
        try:
            path = None
            folder = None
            filename = file.filename
            # print("file_name", filename)
            tr_name = SmartTranslator.smart_translate(
              os.path.splitext(filename)[0])
            # print("tr_name", tr_name)
            tr_data = await tr_service.find_by_name(tr_name)
            if tr_data is None:
                return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                                "message": "Technical regulations not exist",
                                "status": 400
                            }
                )
            tr_req_data = await TR_Req_service.find_by_name(tr_name)
            print("hii",tr_req_data)
            if tr_req_data is not None:
                return JSONResponse(
                        status_code=400,
                        content={
                                "message": f"TR - Req already exist for this file {tr_name} ",
                                "status": 400
                            }
                )
                
            tr_toc_data = await TR_Toc_service.find_by_name(tr_name)
            if tr_toc_data is None:
                 return JSONResponse(
                        status_code=404,
                        content={
                                "message": f"Toc not exist for this file {tr_name} ",
                                "status": 404
                            }
                )
            start_page = None
            end_page = None
            matched_idx = None
            for idx, item in enumerate(tr_toc_data.get("toc_index_data",[])):
                if item.get("section").lower()=="A List of Polyethylene and Polypropylene Products Subject to this Regulation".lower() or item.get("section").lower()=="Supplier s Obligations".lower() or  item.get("section").lower()=="Obligations of the Supplier".lower():
                    start_page = item.get("start_page")
                    end_page = item.get("end_page")
                    matched_idx = idx
            print("start_page", start_page, end_page)
            
            text_scope = {
                "start" : tr_toc_data.get("toc_index_data")[matched_idx]["section"],
                "end" : tr_toc_data.get("toc_index_data")[matched_idx+1]["section"]
                
            }
            print(text_scope)
                    
                
            
          
            
            

            if not file.filename.endswith(
                        (".zip", ".pdf",".docx",".txt")
                    ):

                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "message": "ZIP and PDF only"
                            }
                        )


            
            unique_name = (
                    f"{uuid.uuid4()}_{file.filename}"
                )

            print(
                f"Received file: {file.filename}"
            )

            path = os.path.join(
                BASE_DIR,
                unique_name
            )

            # =========================
            # SAVE FILE (STREAMING) With Validation
            # =========================
            MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000 MB
            CHUNK_SIZE = 1024 * 1024           # 1 MB


            # =========================
            # SAVE FILE (STREAMING)
            # WITH FILE SIZE VALIDATION
            # =========================
            current_size = 0

            async with aiofiles.open(
                path,
                "wb"
            ) as out_file:

                while chunk := await file.read(CHUNK_SIZE):

                    current_size += len(chunk)

                    # =========================
                    # FILE SIZE VALIDATION
                    # =========================
                    if current_size > MAX_FILE_SIZE:

                        # delete partial uploaded file
                        await out_file.close()

                        if os.path.exists(path):
                            os.remove(path)

                        return JSONResponse(
                            {
                                "error": (
                                    "File too large. "
                                    "Maximum allowed size is 500 MB"
                                )
                            },
                            status_code=400
                        )

                    await out_file.write(chunk)


            # ==========================================
            # EXTRACT ZIP
            # ==========================================
            case_id = str(uuid.uuid4())[:8]

            is_zip = file.filename.lower().endswith(
                    ".zip"
                )

                # =========================
                # EXTRACT ZIP
                # =========================
            if is_zip:

                try:

                    folder = await asyncio.to_thread(
                        extract_zip,
                        path,
                        case_id
                    )

                except zipfile.BadZipFile:

                    return JSONResponse(
                        {
                            "error": "Invalid ZIP file"
                        },
                        status_code=400
                    )

                files = await asyncio.to_thread(
                    get_files,
                    folder
                )

            else:

                files = [path]

            # ==========================================
            # PROCESS FILES CONCURRENTLY
            # ==========================================
            tasks = [
                process_tr_hs(f_path, start_page, end_page,text_scope)
                for f_path in files
            ]
            

            processed_results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            print("processed result",len(processed_results))
            if not processed_results:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "File not processes created successfully",
                        "data": processed_results
                    }
                )
            req_data = processed_results[0]
                
            payload = {
                "req_id":  req_data.get("req_id"),
                # "tr_code": req_data.get("tr_code"),
                # "req_raw_data": req_data.get("clean_text"),
                # "tr_requirement": req_data.get("req"),
                # "tr_req_clauses": req_data.get("cluases"),
                "data": req_data.get("data"),
                
                "tr_toc_id": tr_toc_data.get("id"),
                "tr_id": tr_data.get("id"),
                "tr_name": tr_data.get("tr_name")
            }
            # print("payload", payload)
            # tr_req_data = await TR_REQUIREMENTS_Service.create_tr_toc(payload)
        
            

            # ==========================================
            # HANDLE RESULTS
            # ==========================================
        

            return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "message": "TR_Req created successfully",
                        "data": payload
                    }
                )

        except Exception as e:

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": str(e)
                }
            )
        finally:

            # =========================
            # CLEANUP UPLOADED FILE
            # =========================
            if path:

                await asyncio.to_thread(
                    cleanup_file,
                    path
                )

            # =========================
            # CLEANUP EXTRACTED FOLDER
            # =========================
            if folder:

                await asyncio.to_thread(
                    cleanup_folder,
                    folder
                )



      

async def FindTrStd(file: UploadFile = File(...), TR_Req_service: TR_REQUIREMENTS_Service=Depends(get_tr_requirements_service),TR_Toc_service: TR_TOC_Service=Depends(get_tr_toc_service), tr_service:  TechnicalRegulationService =  Depends(
        get_technical_regulation_service
    )):
        try:
            path = None
            folder = None
            filename = file.filename
            # print("file_name", filename)
            tr_name = SmartTranslator.smart_translate(
              os.path.splitext(filename)[0])
            # print("tr_name", tr_name)
            tr_data = await tr_service.find_by_name(tr_name)
            if tr_data is None:
                return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                                "message": "Technical regulations not exist",
                                "status": 400
                            }
                )
            tr_req_data = await TR_Req_service.find_by_name(tr_name)
            print("hii",tr_req_data)
            if tr_req_data is not None:
                return JSONResponse(
                        status_code=400,
                        content={
                                "message": f"TR - Req already exist for this file {tr_name} ",
                                "status": 400
                            }
                )
                
            tr_toc_data = await TR_Toc_service.find_by_name(tr_name)
            if tr_toc_data is None:
                 return JSONResponse(
                        status_code=404,
                        content={
                                "message": f"Toc not exist for this file {tr_name} ",
                                "status": 404
                            }
                )
            start_page = None
            end_page = None
            matched_idx = None
            for idx, item in enumerate(tr_toc_data.get("toc_index_data",[])):
                if item.get("section").lower()=="List of Standards".lower() or item.get("section").lower()=="Supplier s Obligations".lower() or  item.get("section").lower()=="Obligations of the Supplier".lower():
                    start_page = item.get("start_page")
                    end_page = item.get("end_page")
                    matched_idx = idx
            print("start_page", start_page, end_page)
            
            text_scope = {
                "start" : tr_toc_data.get("toc_index_data")[matched_idx]["section"],
                "end" : tr_toc_data.get("toc_index_data")[matched_idx+1]["section"]
                
            }
            print(text_scope)
                    
                
            
          
            
            

            if not file.filename.endswith(
                        (".zip", ".pdf",".docx",".txt")
                    ):

                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "message": "ZIP and PDF only"
                            }
                        )


            
            unique_name = (
                    f"{uuid.uuid4()}_{file.filename}"
                )

            print(
                f"Received file: {file.filename}"
            )

            path = os.path.join(
                BASE_DIR,
                unique_name
            )

            # =========================
            # SAVE FILE (STREAMING) With Validation
            # =========================
            MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1000 MB
            CHUNK_SIZE = 1024 * 1024           # 1 MB


            # =========================
            # SAVE FILE (STREAMING)
            # WITH FILE SIZE VALIDATION
            # =========================
            current_size = 0

            async with aiofiles.open(
                path,
                "wb"
            ) as out_file:

                while chunk := await file.read(CHUNK_SIZE):

                    current_size += len(chunk)

                    # =========================
                    # FILE SIZE VALIDATION
                    # =========================
                    if current_size > MAX_FILE_SIZE:

                        # delete partial uploaded file
                        await out_file.close()

                        if os.path.exists(path):
                            os.remove(path)

                        return JSONResponse(
                            {
                                "error": (
                                    "File too large. "
                                    "Maximum allowed size is 500 MB"
                                )
                            },
                            status_code=400
                        )

                    await out_file.write(chunk)


            # ==========================================
            # EXTRACT ZIP
            # ==========================================
            case_id = str(uuid.uuid4())[:8]

            is_zip = file.filename.lower().endswith(
                    ".zip"
                )

                # =========================
                # EXTRACT ZIP
                # =========================
            if is_zip:

                try:

                    folder = await asyncio.to_thread(
                        extract_zip,
                        path,
                        case_id
                    )

                except zipfile.BadZipFile:

                    return JSONResponse(
                        {
                            "error": "Invalid ZIP file"
                        },
                        status_code=400
                    )

                files = await asyncio.to_thread(
                    get_files,
                    folder
                )

            else:

                files = [path]

            # ==========================================
            # PROCESS FILES CONCURRENTLY
            # ==========================================
            tasks = [
                process_tr_std(f_path, start_page, end_page,text_scope)
                for f_path in files
            ]
            

            processed_results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            print("processed result",len(processed_results))
            if not processed_results:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "File not processes created successfully",
                        "data": processed_results
                    }
                )
            req_data = processed_results[0]
                
            payload = {
                "req_id":  req_data.get("req_id"),
                # "tr_code": req_data.get("tr_code"),
                # "req_raw_data": req_data.get("clean_text"),
                # "tr_requirement": req_data.get("req"),
                # "tr_req_clauses": req_data.get("cluases"),
                "data": req_data.get("data"),
                
                "tr_toc_id": tr_toc_data.get("id"),
                "tr_id": tr_data.get("id"),
                "tr_name": tr_data.get("tr_name")
            }
            # print("payload", payload)
            # tr_req_data = await TR_REQUIREMENTS_Service.create_tr_toc(payload)
        
            

            # ==========================================
            # HANDLE RESULTS
            # ==========================================
        

            return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "message": "TR_Req created successfully",
                        "data": payload
                    }
                )

        except Exception as e:

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": str(e)
                }
            )
        finally:

            # =========================
            # CLEANUP UPLOADED FILE
            # =========================
            if path:

                await asyncio.to_thread(
                    cleanup_file,
                    path
                )

            # =========================
            # CLEANUP EXTRACTED FOLDER
            # =========================
            if folder:

                await asyncio.to_thread(
                    cleanup_folder,
                    folder
                )