from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    JSON
)

from app.models.base_models import BaseMixin
from core.database import Base


class KSAsaleem(Base,BaseMixin):
    __tablename__ = "ksasaleems"

    id = Column(Integer, primary_key=True, index=True)
    ksa_id = Column(String(100), unique=True, index=True, nullable=False)
    ksa_name = Column(String(255), nullable=True)

    

    file_name = Column(String(500), nullable=True)

    # Text Info
    text = Column(Text, nullable=True)


    # Extraction Info

    confidence = Column(Float, default=0.0)

    # JSON Data
    clause = Column(JSON, nullable=True)
    