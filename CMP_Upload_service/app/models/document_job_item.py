import uuid

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Integer,
    Text
)

from sqlalchemy.dialects.postgresql import UUID



from core.database import Base

from .base_models import BaseMixin


class DocumentJobItem(Base, BaseMixin):

    __tablename__ = "document_job_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    parent_job_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "document_jobs.id",
            ondelete="CASCADE"
        )
    )

    module = Column(
        String(100),
        nullable=False
    )

    file_name = Column(
        String,
        nullable=False
    )

    storage_path = Column(
        String,
        nullable=False
    )

    status = Column(
        String(50),
        default="queued"
    )

    # =====================================
    # RETRY COUNT
    # =====================================
    retry_count = Column(
        Integer,
        default=0
    )

    # =====================================
    # ERROR MESSAGE
    # =====================================
    error_message = Column(
        Text,
        nullable=True
    )

