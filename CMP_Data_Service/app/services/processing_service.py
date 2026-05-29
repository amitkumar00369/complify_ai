from app.utils.arbic_char import SmartTranslator
from app.utils.tr_std_ksa_sbr_file_process import (
    process_ksa_saleem,
    process_saber,
    process_std,
    process_tr
)
from app.utils.enum import allowedModules
from .comlplify_file_data_processing import ComplifyDataService
import asyncio,os

class ProcessingService:

    @staticmethod
    async def process_document(
        module,
        file_path
    ):

        if module == allowedModules.saleem.value:

            return await ComplifyDataService.upload_ksa_saleem(
                file_path
            )

        elif module == allowedModules.saber.value:
            saber_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing saber file:", file_path, "with name:", saber_name)
     

            return await ComplifyDataService.upload_saber_service(
                file_path,saber_name
            )
        elif module == allowedModules.hs_code.value:
            source_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing hs-code file:", file_path, "with name:", source_name)
     

            return await ComplifyDataService.import_hs_master_service(
                file_path,source_name
            )
        elif module == allowedModules.saber_cases.value:
            saber_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing saber file:", file_path, "with name:", saber_name)
     

            return await ComplifyDataService.upload_saber_cases_service(
                file_path,saber_name
            )

        elif module == allowedModules.standards.value:

            return await ComplifyDataService.upload_standard_service(
                file_path
            )

        elif module == allowedModules.technical_regulation.value:

            return await ComplifyDataService.upload_technical_regulations_service       (
                file_path
            )

        else:

            raise Exception(
                "Invalid module"
            )