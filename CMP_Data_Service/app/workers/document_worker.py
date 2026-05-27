import asyncio

from app.services.queue_service import (
    queue_service
)

from app.services.processing_service import (
    ProcessingService
)

from app.services.job_service import (
    JobService
)

from app.core.database import (
    AsyncSessionLocal
)


async def start_worker():

    print("Worker started...")

    while True:

        try:

            message = await queue_service.consume()

            print(
                "Received Job:",
                message
            )

            async with AsyncSessionLocal() as db:

                await JobService.update_status(
                    db,
                    message["job_id"],
                    "processing"
                )

                try:

                    result = (
                        await ProcessingService.process_document(
                            module=message["module"],
                            file_path=message["local_path"]
                        )
                    )

                    print(
                        "Processed:",
                        result
                    )

                    await JobService.update_status(
                        db,
                        message["job_id"],
                        "processed"
                    )

                except Exception as e:

                    await JobService.update_status(
                        db,
                        message["job_id"],
                        "failed",
                        str(e)
                    )

                    print("Worker Error:", e)

        except Exception as e:

            print("Queue Error:", e)

        await asyncio.sleep(1)