from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document_job_service import (
    DocumentJobService
)

from app.workers.parent_worker import (
    process_parent_zip
)

from app.workers.child_worker import (
    process_child_file
)


class JobScheduler:

    @staticmethod
    async def process_pending_jobs(
        db: AsyncSession
    ):

        jobs = await (
            DocumentJobService.get_queued_jobs(
                db
            )
        )

        for job in jobs:
            job.status = "scheduled"

        await db.commit()

        for job in jobs:

            if job.file_name.lower().endswith(".zip"):

                process_parent_zip.delay(
                    str(job.id),
                    job.module,
                    job.storage_path
                )

            else:

                process_child_file.delay(
                    None,
                    str(job.id),
                    job.module,
                    job.storage_path,
                    job.file_name
                )