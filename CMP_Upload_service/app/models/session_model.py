from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from app.models.base_models import BaseMixin
from core.database import Base
from ..utils.enum import userType
from datetime import datetime


class Session(Base, BaseMixin):
    __tablename__ = "sessions"  

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_type = Column(Enum(userType), default=userType.user)

    email = Column(String, default="")
    phone_number = Column(String, default="")

    access_token = Column(String, default="")
    refresh_token = Column(String, default="")

    device_id = Column(String, default="")
    device_token = Column(String, default="")
    device_type_id = Column(String, default="")