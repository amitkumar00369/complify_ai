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


class Technical_regulation(Base,BaseMixin):
    __tablename__ = "technical_regulations"

    id = Column(Integer, primary_key=True, index=True)
    tr_id = Column(String(100), unique=True, index=True, nullable=False)
    tr_name = Column(String(255), nullable=True)


    file_name = Column(String(500), nullable=True)

    # Text Info
    text = Column(Text, nullable=True)

    # JSON Data
    meta_json = Column(JSON, nullable=True)
    