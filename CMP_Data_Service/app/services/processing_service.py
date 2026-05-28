from app.utils.arbic_char import SmartTranslator
from app.utils.tr_std_ksa_sbr_file_process import (
    process_ksa_saleem,
    process_saber,
    process_std,
    process_tr
)
from .comlplify_file_data_processing import ComplifyDataService
import asyncio,os

class ProcessingService:

    @staticmethod
    async def process_document(
        module,
        file_path
    ):

        if module == "saleem":

            return await ComplifyDataService.upload_ksa_saleem(
                file_path
            )

        elif module == "saber":
            saber_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing saber file:", file_path, "with name:", saber_name)
     

            return await ComplifyDataService.upload_saber_service(
                file_path,saber_name
            )
        elif module == "hs-code":
            saber_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing saber file:", file_path, "with name:", saber_name)
     

            return await ComplifyDataService.import_hs_master_service(
                file_path
            )
        elif module == "saber-cases":
            saber_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing saber file:", file_path, "with name:", saber_name)
     

            return await ComplifyDataService.upload_saber_cases_service(
                file_path,saber_name
            )

        elif module == "standards":

            return await ComplifyDataService.upload_standard_service(
                file_path
            )

        elif module == "technical-regulation":

            return await ComplifyDataService.upload_technical_regulations_service       (
                file_path
            )

        else:

            raise Exception(
                "Invalid module"
            )