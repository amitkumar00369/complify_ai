
from app.utils.data_processing_for_schema import ResponseBuilder
import os
import json
import uuid
import asyncio
import aiofiles
import zipfile
from starlette import status
from fastapi import (
    UploadFile,
    File,Depends
)

from fastapi.responses import JSONResponse

from app.utils.tr_std_ksa_sbr_file_process import (
    process_saber
)

from app.utils.zip_file import (
    BASE_DIR,
    extract_zip,
    get_files,cleanup_file,cleanup_folder
)


from app.services.saber_service import SaberService,get_saber_service

# ==========================================
# UPLOAD SABER
# ==========================================
async def upload_saber(
    file: UploadFile = File(...), saber_service: SaberService = Depends(get_saber_service )
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
        MAX_FILE_SIZE = 1000 * 1024 * 1024  # 500 MB
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
            process_saber(f_path)
            for f_path in files
        ]
        

        processed_results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )
        print("processed result",len(processed_results))
        docs = await ResponseBuilder.buildResponseOfSaber(processed_results)
        
        saber_data =await saber_service.create_saber_in_bulk(docs)
        

        # ==========================================
        # HANDLE RESULTS
        # ==========================================
    

        return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Saber created successfully",
                    "data": saber_data
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
# GET SABER DATA
# ==========================================
async def get_saber():

    json_path = "saber_results.json"

    if os.path.exists(json_path):

        print(
            f"Loading Saber results "
            f"from {json_path}..."
        )

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as f:

            print(
                f"size of Saber results file: "
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