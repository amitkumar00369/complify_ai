from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,
    Float,
    Boolean,
    ForeignKey
)

from app.models.base_models import BaseMixin
from core.database import Base


class ProductFileInfo(Base, BaseMixin):

    __tablename__ = "products_file_info"

    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # RELATION
    # =========================

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=True
    )

    # =========================
    # FILE INFO
    # =========================

    file_name = Column(String(500), nullable=True)

    file_path = Column(Text, nullable=True)

    file_type = Column(String(50), nullable=True)

    file_hash = Column(String(255), nullable=True)

    # =========================
    # VALIDATION
    # =========================

    confidence_score = Column(Float, nullable=True)

    is_valid = Column(Boolean, default=False)

    # =========================
    # OCR / TEXT
    # =========================

    text = Column(Text, nullable=True)

    text_length = Column(Integer, nullable=True)

    # =========================
    # EXTRACTION DATA
    # =========================

    visual_data = Column(JSON, nullable=True)

    clause_data = Column(JSON, nullable=True)

    # =========================
    # META
    # =========================

    sub_folder_name = Column(String(500), nullable=True)

    product_info = Column(Text, nullable=True)