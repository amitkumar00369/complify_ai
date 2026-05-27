# app/services/document_job_item_service.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from sqlalchemy import func

from app.models.document_job_item import (
    DocumentJobItem
)


class DocumentJobItemService:

    # ==========================================
    # CREATE JOB ITEM
    # ==========================================
    @staticmethod
    async def create_job_item(
        db: AsyncSession,
        payload: dict
    ):

        job_item = DocumentJobItem(

            parent_job_id=payload.get(
                "parent_job_id"
            ),

            module=payload.get(
                "module"
            ),

            file_name=payload.get(
                "file_name"
            ),

            storage_path=payload.get(
                "storage_path"
            ),

            status=payload.get(
                "status",
                "queued"
            ),

            retry_count=payload.get(
                "retry_count",
                0
            ),

            error_message=payload.get(
                "error_message"
            )
        )

        db.add(job_item)

        await db.commit()

        await db.refresh(job_item)

        return job_item

    # ==========================================
    # GET BY ID
    # ==========================================
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        job_item_id
    ):

        result = await db.execute(

            select(DocumentJobItem).where(
                DocumentJobItem.id
                == job_item_id
            )
        )

        return result.scalar_one_or_none()

    # ==========================================
    # UPDATE STATUS
    # ==========================================
    @staticmethod
    async def update_status(
        db: AsyncSession,
        job_item_id,
        status,
        error_message=None
    ):

        result = await db.execute(

            select(DocumentJobItem).where(
                DocumentJobItem.id
                == job_item_id
            )
        )

        job_item = result.scalar_one_or_none()

        if not job_item:

            return None

        job_item.status = status

        if error_message:

            job_item.error_message = (
                error_message
            )

        await db.commit()

        await db.refresh(job_item)

        return job_item

    # ==========================================
    # UPDATE STORAGE PATH
    # ==========================================
    @staticmethod
    async def update_storage_path(
        db: AsyncSession,
        job_item_id,
        storage_path
    ):

        result = await db.execute(

            select(DocumentJobItem).where(
                DocumentJobItem.id
                == job_item_id
            )
        )

        job_item = result.scalar_one_or_none()

        if not job_item:

            return None

        job_item.storage_path = (
            storage_path
        )

        await db.commit()

        await db.refresh(job_item)

        return job_item

    # ==========================================
    # UPDATE RETRY COUNT
    # ==========================================
    @staticmethod
    async def increment_retry_count(
        db: AsyncSession,
        job_item_id
    ):

        result = await db.execute(

            select(DocumentJobItem).where(
                DocumentJobItem.id
                == job_item_id
            )
        )

        job_item = result.scalar_one_or_none()

        if not job_item:

            return None

        job_item.retry_count += 1

        await db.commit()

        await db.refresh(job_item)

        return job_item

    # ==========================================
    # GET PARENT JOB ITEMS
    # ==========================================
    @staticmethod
    async def get_parent_job_items(
        db: AsyncSession,
        parent_job_id
    ):

        result = await db.execute(

            select(DocumentJobItem).where(
                DocumentJobItem.parent_job_id
                == parent_job_id
            )
        )

        return result.scalars().all()

    # ==========================================
    # GET JOB COUNTS
    # ==========================================
    @staticmethod
    async def get_job_counts(
        db: AsyncSession,
        parent_job_id
    ):

        result = await db.execute(

            select(
                DocumentJobItem.status,
                func.count(
                    DocumentJobItem.id
                )
            ).where(
                DocumentJobItem.parent_job_id
                == parent_job_id
            ).group_by(
                DocumentJobItem.status
            )
        )

        rows = result.all()

        return {
            row[0]: row[1]
            for row in rows
        }

    # ==========================================
    # DELETE JOB ITEM
    # ==========================================
    @staticmethod
    async def delete_job_item(
        db: AsyncSession,
        job_item_id
    ):

        result = await db.execute(

            select(DocumentJobItem).where(
                DocumentJobItem.id
                == job_item_id
            )
        )

        job_item = result.scalar_one_or_none()

        if not job_item:

            return False

        await db.delete(job_item)

        await db.commit()

        return True