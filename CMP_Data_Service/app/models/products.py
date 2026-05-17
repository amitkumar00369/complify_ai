from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,ForeignKey
)

from app.models.base_models import BaseMixin
from core.database import Base


class Product(Base, BaseMixin):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # BASIC INFO
    # =========================

    case_id = Column(
        String,
        index=True
    )

    product_name = Column(
        Text,
        nullable=True,
        unique=True,
        index=True
    )

    folder_name = Column(
        Text,
        nullable=True
    )

    standard_name = Column(
        Text,
        nullable=True
    )

    hs_code = Column(
        String,
        nullable=True,
        index=True
    )

    hs_code_4 = Column(
        String,
        nullable=True,
        index=True
    )

    # =========================
    # JSON DATA
    # =========================

    model_names = Column(
        JSON,
        nullable=True
    )

    pcoc_data = Column(
        JSON,
        nullable=True
    )

    products_file_info = Column(
        JSON,
        nullable=True
    )    
    tr_id = Column(Integer, ForeignKey("technical_regulations.id"), nullable=True)
    tr_name = Column(String(255),  nullable = True)
    
    std_id = Column(Integer, ForeignKey("standards.id"), nullable=True)
    std_name = Column(String(255),nullable = True)