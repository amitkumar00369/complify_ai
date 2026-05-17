from sqlalchemy import Column, BigInteger, String, Text, Boolean, Date, DateTime,ForeignKey,Integer
from sqlalchemy.sql import func
from core.database import Base
from app.models.base_models import BaseMixin


class HSMaster(Base,BaseMixin):
    __tablename__ = "hs_master"

    id = Column(BigInteger, primary_key=True, index=True)

    full_hs_code = Column(String(12), unique=True, nullable=False, index=True)

    chapter_code = Column(String(2), nullable=True, index=True)
    heading_code = Column(String(4), nullable=True, index=True)
    subheading_code = Column(String(6), nullable=True, index=True)

    item_name_en = Column(Text)
    item_name_ar = Column(Text)

    duty_rate_en = Column(String(50))
    duty_rate_ar = Column(String(50))
    procedure_codes = Column(String(100))

    effective_date = Column(Date)

    source_file = Column(String(255))
    source_sheet = Column(String(100))
    source_row = Column(BigInteger)
     # map with product, Technical regulation, standard
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(255),  nullable = True)
    
    tr_id = Column(Integer, ForeignKey("technical_regulations.id"), nullable=True)
    tr_name = Column(String(255),  nullable = True)
    
    std_id = Column(Integer, ForeignKey("standards.id"), nullable=True)
    std_name = Column(String(255), nullable = True)

    is_active = Column(Boolean, default=True)
