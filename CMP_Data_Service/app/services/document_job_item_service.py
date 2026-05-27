from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_job_items import (
    DocumentJobItem
)


class DocumentJobItemService:

    @staticmethod
    async def create_item(
        db: AsyncSession,
        payload: dict
    ):

        item = DocumentJobItem(
            parent_job_id=payload["parent_job_id"],
            module=payload["module"],
            file_name=payload["file_name"],
            original_file_name=payload.get(
                "original_file_name"
            ),
            s3_key=payload["s3_key"],
            file_size=payload.get(
                "file_size",
                0
            ),
            file_type=payload.get(
                "file_type"
            ),
            status="queued"
        )

        db.add(item)

        await db.commit()

        await db.refresh(item)

        return item

    @staticmethod
    async def update_status(
        db: AsyncSession,
        item_id,
        status,
        error_message=None,
        extracted_method=None,
        confidence=None
    ):

        query = select(
            DocumentJobItem
        ).where(
            DocumentJobItem.id == item_id
        )

        result = await db.execute(query)

        item = result.scalar_one_or_none()

        if not item:
            return None

        item.status = status

        if error_message:
            item.error_message = error_message

        if extracted_method:
            item.extracted_method = (
                extracted_method
            )

        if confidence:
            item.confidence = confidence

        await db.commit()

        await db.refresh(item)

        return item

    @staticmethod
    async def get_items_by_parent(
        db: AsyncSession,
        parent_job_id
    ):

        query = select(
            DocumentJobItem
        ).where(
            DocumentJobItem.parent_job_id
            == parent_job_id
        )

        result = await db.execute(query)

        return result.scalars().all()