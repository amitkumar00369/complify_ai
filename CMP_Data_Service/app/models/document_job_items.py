import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    BigInteger,
    Numeric
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from core.database import Base

from app.models.base_models import BaseMixin


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
        ),
        nullable=False
    )

    module = Column(
        String(100),
        nullable=False
    )

    file_name = Column(
        String,
        nullable=False
    )

    original_file_name = Column(
        String,
        nullable=True
    )

    s3_key = Column(
        String,
        nullable=False
    )

    file_size = Column(
        BigInteger,
        default=0
    )

    file_type = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(50),
        default="queued"
    )

    retry_count = Column(
        Integer,
        default=0
    )

    error_message = Column(
        Text,
        nullable=True
    )

    extracted_method = Column(
        String(100),
        nullable=True
    )

    confidence = Column(
        Numeric(5, 2),
        default=0
    )

    processing_started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    processing_completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

  

   

    # relationship
    parent_job = relationship(
        "DocumentJob",
        backref="items"
    )