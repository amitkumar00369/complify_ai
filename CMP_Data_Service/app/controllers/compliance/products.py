from fastapi import UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette import status
from app.utils.data_processing_for_schema import ResponseBuilder
import os
import uuid
import asyncio
import aiofiles
import zipfile
from app.utils.zip_file import (
    BASE_DIR,
    extract_zip,
    get_files,
    save_file,cleanup_file,cleanup_folder
)

from app.utils.item_file_processor import (
    process_documents,tr_data,std_data
)

from app.services.product_item_servce import (
    ProductService,
    get_product_service
)
from app.services.technical_regulation_service import (
    TechnicalRegulationService,
    get_technical_regulation_service
)
from app.services.standard_service import (
    StandardService,
    get_standard_service
)
from sqlalchemy.ext.asyncio import AsyncSession

#from app.services.llama_service import databyhscode_usingllm

from core.database import get_db
from app.services.hs_code_service import HSCodeService

# =========================
# UPLOAD CASE
# =========================
async def upload_case(

    file: UploadFile = File(...),

    product_service: ProductService = Depends(
        get_product_service
    ),
    tr__service: TechnicalRegulationService = Depends(
        get_technical_regulation_service
    ),
    std_service: StandardService = Depends(
        get_standard_service
    ),
    db: AsyncSession = Depends(get_db)
):

    try:
        path = None
        folder = None

        zip_name = file.filename.split(".")[0]
        
        print("name of file",zip_name)

        if not file.filename.endswith(
            (".zip", ".pdf")
        ):

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "ZIP and PDF only",
                    "status": 400
                }
            )
        ItemExist = await product_service.get_by_product_name(zip_name)

        if ItemExist is not None:

            print("type:", type(ItemExist))

            if isinstance(ItemExist, dict):
                print("keys:", ItemExist.keys())

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Item already exist"
                }
            )
        # =========================
        # SAVE FILE
        # =========================

        unique_name = (
            f"{uuid.uuid4()}_{file.filename}"
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

        # =========================
        # CASE ID
        # =========================

        case_id = str(uuid.uuid4())[:8]

        # =========================
        # EXTRACT
        # =========================

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

        # =========================
        # PROCESS DOCUMENTS
        # =========================

        process_docs = await process_documents(
            files,
            file_name=zip_name
        )

        docs = await ResponseBuilder.buildResponseOfProduct(process_docs)
        # return docs
        # file_data = await ResponseBuilder.prepare_file_info_data(4, docs.get("productsFileInfo"))
        # return file_data
        

        # =========================
        # CHECK EXISTING PRODUCT
        # =========================

        existing_product = await product_service.get_by_product_name(
            docs.get("product_name")
        )

        # =========================
        # UPDATE EXISTING PRODUCT
        # =========================

        if existing_product:

            existing_files = existing_product.get(
                "products_file_info",
                []
            )

            incoming_files = docs.get(
                "productsFileInfo",
                []
            )

            file_map = {
                f.get("file_name"): idx
                for idx, f in enumerate(existing_files)
            }

            for file_item in incoming_files:

                file_name = file_item.get(
                    "file_name"
                )

                if file_name in file_map:

                    existing_files[
                        file_map[file_name]
                    ] = file_item

                else:

                    existing_files.append(
                        file_item
                    )

            update_payload = {
                "products_file_info": existing_files
            }

            updated_product = await product_service.find_by_id_update(
                existing_product["id"],
                update_payload
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Product updated successfully",
                    "data": updated_product
                }
            )

        # =========================
        # CREATE NEW PRODUCT
        # =========================
        allTrData = await tr__service.get_all()
        print("alltrdata",len(allTrData))
        trdata = await tr_data(docs.get("hs_code"),allTrData)
        print("tddata", trdata)
        allStdData = await std_service.get_all()
        print("allStdData",len(allStdData))
        
        stddata = await std_data(docs.get("product_name"),allStdData)
        print("stddata",stddata)
        if  not docs.get("standard_name"):
            print("yesssss")
            docs["standard_name"] = stddata["std_name"]
            

        payload = {
            "case_id": docs.get("caseId"),
            "product_name": docs.get("product_name"),
            "folder_name": docs.get("folder_name"),
            "standard_name": docs.get("standard_name"),
            "hs_code": docs.get("hs_code"),
            "hs_code_4": docs.get("hsCode_4"),
            "model_names": docs.get("modelName"),
            "pcoc_data": docs.get("pcocData"),
            "products_file_info": docs.get(
                "productsFileInfo"
            ),
            "tr_id": trdata.get("tr_id"),
            "tr_name": trdata.get("tr_name"),
            "std_id": stddata.get("std_id"),
            "std_name": stddata.get("std_name")
        }
        print("keys", payload.keys())

        new_product = await product_service.create_product(
            payload
        )
        hs_data = await HSCodeService.findOneAndUpdate(db,docs.get("hs_code"), new_product)
        

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Product created successfully",
                "data": new_product,
                "hs": hs_data
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
async def getDetailsById(

    product_id: int,

    product_service: ProductService = Depends(
        get_product_service
    )
):

    try:

        product = await product_service.find_by_id(
            product_id
        )

        if not product:

            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "Product not found"
                }
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Product fetched successfully",
                "data": product
            }
        )

    except Exception as e:

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": str(e)
            }
        )


# =========================
# GET PRODUCT LIST
# =========================
async def getList(

    page: int = 1,

    limit: int = 10,

    product_service: ProductService = Depends(
        get_product_service
    )
):

    try:

        products = await product_service.get_list(
            option={
                "page": page,
                "limit": limit
            }
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Products fetched successfully",
                "data": products
            }
        )

    except Exception as e:

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": str(e)
            }
        )