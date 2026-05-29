from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_models import BaseMixin
from core.database import Base


class Document(Base, BaseMixin):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(String, unique=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    file_path = Column(String, nullable=True)
    file_type = Column(String, nullable=True)

    hash_key = Column(String, nullable=True)

    # Relationship
    product = relationship("Product", backref="documents")