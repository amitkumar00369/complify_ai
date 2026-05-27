from app.utils.arbic_char import SmartTranslator
from app.utils.tr_std_ksa_sbr_file_process import (
    process_ksa_saleem,
    process_saber,
    process_std,
    process_tr
)
import asyncio,os

class ProcessingService:

    @staticmethod
    async def process_document(
        module,
        file_path
    ):

        if module == "saleem":

            return await process_ksa_saleem(
                file_path
            )

        elif module == "saber":
            saber_name = SmartTranslator.smart_translate(
            os.path.splitext(
                os.path.basename(file_path)
            )[0]
        )
            print("Processing saber file:", file_path, "with name:", saber_name)
        #     tasks = [
        #     await process_saber(f_path,saber_name)
        #     for f_path in file_path
        # ]
        

        #     processed_results = await asyncio.gather(
        #         *tasks,
        #         return_exceptions=True
        #     )
        #     print("processed result",len(processed_results))
        #     return processed_results

            return await process_saber(
                file_path,saber_name
            )

        elif module == "standards":

            return await process_std(
                file_path
            )

        elif module == "technical-regulation":

            return await process_tr(
                file_path
            )

        else:

            raise Exception(
                "Invalid module"
            )