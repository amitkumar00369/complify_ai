from app.services.processing_service import (
    ProcessingService
)

from app.services.document_job_item_service import (
    DocumentJobItemService
)

from app.services.s3_service import (
    s3_service
)


async def process_child_job(
    db,
    item
):

    try:

        # update processing
        await (
            DocumentJobItemService.update_status(
                db,
                item.id,
                "processing"
            )
        )

        # download s3 file
        local_file = (
            await s3_service.download_file(
                item.s3_key
            )
        )

        # process
        result = (
            await ProcessingService.process_document(
                item.module,
                local_file
            )
        )

        # success
        await (
            DocumentJobItemService.update_status(
                db,
                item.id,
                "processed",
                extracted_method=result.get(
                    "extrated_method"
                ),
                confidence=result.get(
                    "confidence",
                    0
                )
            )
        )

    except Exception as e:

        await (
            DocumentJobItemService.update_status(
                db,
                item.id,
                "failed",
                error_message=str(e)
            )
        )