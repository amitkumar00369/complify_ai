import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime
)
from sqlalchemy import Text

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func

from core.database import Base
from .base_models import BaseMixin


class DocumentJob(Base, BaseMixin):

    __tablename__ = "document_jobs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
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

    total_files = Column(
        Integer,
        default=0
    )

    processed_files = Column(
        Integer,
        default=0
    )

    failed_files = Column(
        Integer,
        default=0
    )
    file_hash = Column(
    Text,
    nullable=True,
    index=True
)

    