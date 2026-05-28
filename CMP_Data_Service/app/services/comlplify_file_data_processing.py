
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal

from app.services.hs_code_service import HSCodeService

from app.utils.data_processing_for_schema import (
    ResponseBuilder
)

from app.utils.tr_std_ksa_sbr_file_process import (
    process_ksa_saleem,
    process_saber,
    process_tr,
    process_std
)

from app.utils.item_file_processor import (
    process_documents,
    tr_data,
    std_data
)

from app.services.ksa_saleem_service import (
    KSASaleemService
)

from app.services.product_item_servce import (
    ProductService
)

from app.services.technical_regulation_service import (
    TechnicalRegulationService
)

from app.services.standard_service import (
    StandardService
)

from app.services.saber_service import (
    SaberService
)


class ComplifyDataService:

    # ==========================================
    # IMPORT HS MASTER
    # ==========================================
    @staticmethod
    async def import_hs_master_service(
        file
    ):

        async with AsyncSessionLocal() as db:

            return await (
                HSCodeService.import_hs_master_into_table(
                    db,
                    file
                )
            )

    # ==========================================
    # UPLOAD KSA SALEEM
    # ==========================================
    @staticmethod
    async def upload_ksa_saleem(
        file,
        saber_name: str = None
    ):

        async with AsyncSessionLocal() as db:

            ksa_service = (
                KSASaleemService(db)
            )

            files = [file]

            tasks = [
                process_ksa_saleem(
                    f_path,
                    saber_name
                )
                for f_path in files
            ]

            processed_results = (
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )
            )

            docs = await (
                ResponseBuilder.buildResponseOfKsaSaleem(
                    processed_results
                )
            )

            return await (
                ksa_service.create_ksa_saleem_in_bulk(
                    docs
                )
            )

    # ==========================================
    # UPLOAD SABER CASES
    # ==========================================
    @staticmethod
    async def upload_saber_cases_service(
        path,
        zip_name: str
    ):

        async with AsyncSessionLocal() as db:

            product_service = (
                ProductService(db)
            )

            tr_service = (
                TechnicalRegulationService(db)
            )

            std_service = (
                StandardService(db)
            )

            item_exist = await (
                product_service.get_by_product_name(
                    zip_name
                )
            )

            if item_exist:

                return {
                    "message": (
                        "Item already exist"
                    )
                }

            files = [path]

            process_docs = (
                await process_documents(
                    files,
                    file_name=zip_name
                )
            )

            docs = await (
                ResponseBuilder.buildResponseOfProduct(
                    process_docs
                )
            )

            existing_product = await (
                product_service.get_by_product_name(
                    docs.get(
                        "product_name"
                    )
                )
            )

            # ==================================
            # UPDATE EXISTING PRODUCT
            # ==================================
            if existing_product:

                existing_files = (
                    existing_product.get(
                        "products_file_info",
                        []
                    )
                )

                incoming_files = docs.get(
                    "productsFileInfo",
                    []
                )

                file_map = {
                    f.get("file_name"): idx
                    for idx, f in enumerate(
                        existing_files
                    )
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
                    "products_file_info":
                    existing_files
                }

                return await (
                    product_service.find_by_id_update(
                        existing_product["id"],
                        update_payload
                    )
                )

            # ==================================
            # CREATE NEW PRODUCT
            # ==================================
            all_tr_data = (
                await tr_service.get_all()
            )

            trdata = await tr_data(
                docs.get("hs_code"),
                all_tr_data
            )

            all_std_data = (
                await std_service.get_all()
            )

            stddata = await std_data(
                docs.get("product_name"),
                all_std_data
            )

            if not docs.get(
                "standard_name"
            ):

                docs["standard_name"] = (
                    stddata["std_name"]
                )

            payload = {

                "case_id":
                docs.get("caseId"),

                "product_name":
                docs.get("product_name"),

                "folder_name":
                docs.get("folder_name"),

                "standard_name":
                docs.get("standard_name"),

                "hs_code":
                docs.get("hs_code"),

                "hs_code_4":
                docs.get("hsCode_4"),

                "model_names":
                docs.get("modelName"),

                "pcoc_data":
                docs.get("pcocData"),

                "products_file_info":
                docs.get(
                    "productsFileInfo"
                ),

                "tr_id":
                trdata.get("tr_id"),

                "tr_name":
                trdata.get("tr_name"),

                "std_id":
                stddata.get("std_id"),

                "std_name":
                stddata.get("std_name")
            }

            new_product = await (
                product_service.create_product(
                    payload
                )
            )

            await (
                HSCodeService.findOneAndUpdate(
                    db,
                    docs.get("hs_code"),
                    new_product
                )
            )

            return new_product

    # ==========================================
    # UPLOAD SABER
    # ==========================================
    @staticmethod
    async def upload_saber_service(
        path,
        saber_name: str
    ):

        async with AsyncSessionLocal() as db:

            saber_service = (
                SaberService(db)
            )

            files = [path]

            tasks = [
                process_saber(
                    f_path,
                    saber_name
                )
                for f_path in files
            ]

            processed_results = (
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )
            )

            docs = await (
                ResponseBuilder.buildResponseOfSaber(
                    processed_results
                )
            )

            return await (
                saber_service.create_saber_in_bulk(
                    docs
                )
            )

    # ==========================================
    # UPLOAD TECHNICAL REGULATION
    # ==========================================
    @staticmethod
    async def upload_technical_regulations_service(
        path: str
    ):

        async with AsyncSessionLocal() as db:
            print(
                f"Received file for TR: {path}"
                )

            tr_service = (
                TechnicalRegulationService(db)
            )

            files = [path]

            tasks = [
                process_tr(f_path)
                for f_path in files
            ]

            processed_results = (
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )
            )
            # with open("tr_processing_log.txt", "w") as log_file:
            #     log_file.write(
            #         f"Processed {len(processed_results)} TR files from {path}\n"
            #     )
            #     for idx, result in enumerate(processed_results):
            #         log_file.write(
            #             f"Result {idx+1}:\n{result}\n\n"
            #         )

            docs = await (
                ResponseBuilder.buildResponseOfTechnicalRegulation(
                    processed_results
                )
            )
            print(
                f"Built TR docs, count: {len(docs)}"
            )

            return await (
                tr_service.create_tr_in_bulk(
                    docs
                )
            )

    # ==========================================
    # UPLOAD STANDARD
    # ==========================================
    @staticmethod
    async def upload_standard_service(
        path: str
    ):

        async with AsyncSessionLocal() as db:

            std_service = (
                StandardService(db)
            )

            print(
                f"Received file: {path}"
            )

            files = [path]

            tasks = [
                process_std(f_path)
                for f_path in files
            ]

            processed_results = (
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )
            )

            docs = await (
                ResponseBuilder.buildResponseOfStandard(
                    processed_results
                )
            )

            return await (
                std_service.create_standard_in_bulk(
                    docs
                )
            )

