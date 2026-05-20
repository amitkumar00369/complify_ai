from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,ForeignKey
)

from app.models.base_models import BaseMixin
from core.database import Base


class TR_TOC(Base, BaseMixin):
    __tablename__ = "tr_tocs"

    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # BASIC INFO
    # =========================

    tr_toc_id = Column(
        String,
        index=True
    )

    toc_index_data= Column(
        JSON,
        nullable=True
    )    
    tr_id = Column(Integer, ForeignKey("technical_regulations.id"), nullable=True)
    tr_name = Column(String(255),  nullable = True)
    