from app.utils.tr_std_ksa_sbr_file_process import (
    process_ksa_saleem,
    process_saber,
    process_std,
    process_tr,
    process_item
)
from app.utils.item_file_processor import (
    process_documents,tr_data,std_data
)
from .enum import moduleType

class ProcessingService:

    @staticmethod
    async def process_document(
        module,
        file_path
    ):

        if module == moduleType.saleem:

            return await process_ksa_saleem(
                file_path
            )

        elif module == moduleType.saber:

            return await process_saber(
                file_path
            )

        elif module == moduleType.standards:

            return await process_std(
                file_path
            )

        elif module == moduleType.technicalRegulation:

            return await process_tr(
                file_path
            )
        elif module == moduleType.item:

            return await process_documents(
                file_path
            )

        else:

            raise Exception(
                "Invalid module"
            )