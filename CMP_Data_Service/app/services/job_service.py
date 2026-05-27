from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_model import DocumentJob


class JobService:

    @staticmethod
    async def create_job(
        db: AsyncSession,
        payload: dict
    ):

        job = DocumentJob(
            module=payload["module"],
            file_name=payload["file_name"],
            s3_key=payload["s3_key"],
            status="queued"
        )

        db.add(job)

        await db.commit()

        await db.refresh(job)

        return job

    @staticmethod
    async def update_status(
        db: AsyncSession,
        job_id,
        status,
        error_message=None
    ):

        query = select(DocumentJob).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(query)

        job = result.scalar_one_or_none()

        if not job:
            return None

        job.status = status

        if error_message:
            job.error_message = error_message

        await db.commit()

        await db.refresh(job)

        return job

    @staticmethod
    async def get_job(
        db: AsyncSession,
        job_id
    ):

        query = select(DocumentJob).where(
            DocumentJob.id == job_id
        )

        result = await db.execute(query)

        return result.scalar_one_or_none()