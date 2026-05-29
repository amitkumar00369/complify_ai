from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,ForeignKey
)

from app.models.base_models import BaseMixin
from core.database import Base


class TR_REQUIREMENTS(Base, BaseMixin):
    __tablename__ = "tr_rerquirements"

    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # BASIC INFO
    # =========================

    req_id = Column(
        String,
        index=True
    )
    req_raw_data = Column(Text, nullable=True)

    tr_requirement = Column(
        JSON,
        nullable=True
    )  
    tr_req_clauses = Column(
        JSON,
        nullable=True
    )
    tr_toc_id = Column(Integer, ForeignKey("tr_tocs.id"), nullable=True)
    tr_id = Column(Integer, ForeignKey("technical_regulations.id"), nullable=True)
    tr_name = Column(String(255),  nullable = True)
    