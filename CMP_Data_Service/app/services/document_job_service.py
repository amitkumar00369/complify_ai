from sqlalchemy import (
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.document_job import (
    DocumentJob
)


class DocumentJobService:

    # ==========================================
    # CREATE JOB
    # ==========================================
    @staticmethod
    async def create_job(
        db: AsyncSession,
        payload: dict
    ):

        job = DocumentJob( id=payload.get("id"), module=payload["module"], file_name=payload["file_name"], s3_key=payload["s3_key"], file_hash=payload.get( "file_hash" ), status="queued", total_files=payload.get( "total_files", 0 ), processed_files=0, failed_files=0 )

        db.add(job)

        await db.commit()

        await db.refresh(job)

        return job

    # ==========================================
    # UPDATE STATUS
    # ==========================================
    @staticmethod
    async def update_status(
        db: AsyncSession,
        job_id,
        status,
        error_message=None
    ):

        query = select(
            DocumentJob
        ).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(
            query
        )

        job = result.scalar_one_or_none()

        if not job:

            return None

        job.status = status

        if error_message:

            job.error_message = (
                error_message
            )

        await db.commit()

        await db.refresh(job)

        return job

    # ==========================================
    # GET JOB
    # ==========================================
    @staticmethod
    async def get_job(
        db: AsyncSession,
        job_id
    ):

        query = select(
            DocumentJob
        ).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(
            query
        )

        return result.scalar_one_or_none()

    # ==========================================
    # UPDATE TOTAL FILES
    # ==========================================
    @staticmethod
    async def update_total_files(
        db: AsyncSession,
        job_id,
        total_files
    ):

        query = select(
            DocumentJob
        ).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(
            query
        )

        job = result.scalar_one_or_none()

        if not job:

            return None

        job.total_files = total_files

        await db.commit()

        await db.refresh(job)

        return job

    # ==========================================
    # INCREMENT PROCESSED FILES
    # ==========================================
    @staticmethod
    async def increment_processed_files(
        db: AsyncSession,
        job_id
    ):

        query = select(
            DocumentJob
        ).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(
            query
        )

        job = result.scalar_one_or_none()

        if not job:

            return None

        job.processed_files += 1

        # ==============================
        # AUTO COMPLETE
        # ==============================
        if (
            job.processed_files
            + job.failed_files
        ) >= job.total_files:

            job.status = "completed"

        await db.commit()

        await db.refresh(job)

        return job

    # ==========================================
    # INCREMENT FAILED FILES
    # ==========================================
    @staticmethod
    async def increment_failed_files(
        db: AsyncSession,
        job_id
    ):

        query = select(
            DocumentJob
        ).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(
            query
        )

        job = result.scalar_one_or_none()

        if not job:

            return None

        job.failed_files += 1

        # ==============================
        # AUTO COMPLETE
        # ==============================
        if (
            job.processed_files
            + job.failed_files
        ) >= job.total_files:

            if job.processed_files > 0:

                job.status = (
                    "partially_completed"
                )

            else:

                job.status = "failed"

        await db.commit()

        await db.refresh(job)

        return job
        
    @staticmethod
    async def get_by_hash(
        db,
        file_hash
    ):

        query = select(
            DocumentJob
        ).where(
            DocumentJob.file_hash
            == file_hash
        )

        result = await db.execute(
            query
        )

        return result.scalar_one_or_none()
    @staticmethod
    async def get_queued_jobs(db):

        result = await db.execute(
            select(DocumentJob)
            .where(
                DocumentJob.status == "queued"
            )
            .limit(50)
        )

        return result.scalars().all()