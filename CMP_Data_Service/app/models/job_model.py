import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Integer,
    BigInteger
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func

from core.database import Base

from app.models.base_models import BaseMixin


class DocumentJob(Base, BaseMixin):

    __tablename__ = "document_jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # saleem / saber / standards / tr
    module = Column(
        String(100),
        nullable=False
    )

    # uploaded zip name
    file_name = Column(
        String,
        nullable=False
    )

    # original uploaded s3 path
    s3_key = Column(
        String,
        nullable=False
    )

    # zip / single
    job_type = Column(
        String(50),
        default="zip"
    )

    # queued / processing / completed / failed
    status = Column(
        String(50),
        default="queued"
    )

    # total extracted files
    total_files = Column(
        Integer,
        default=0
    )

    # processed child files
    processed_files = Column(
        Integer,
        default=0
    )

    # failed child files
    failed_files = Column(
        Integer,
        default=0
    )

    # retry count
    retry_count = Column(
        Integer,
        default=0
    )

    # file size
    file_size = Column(
        BigInteger,
        default=0
    )

    # error logs
    error_message = Column(
        Text,
        nullable=True
    )

    # worker started
    processing_started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # worker completed
    processing_completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    