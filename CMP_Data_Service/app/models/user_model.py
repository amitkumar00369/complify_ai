from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from app.models.base_models import BaseMixin
from core.database import Base
from datetime import datetime
from ..utils.enum import userType


class User(Base, BaseMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True, unique=True)

    email = Column(String, unique=True, index=True)
    password = Column(String)

    phone_number = Column(String, nullable=True)
    country_code = Column(String, nullable=True, default="+971")

    is_email_otp_verified = Column(Boolean, default=False)
    email_expire_at = Column(DateTime, nullable=True)

    is_phone_otp_verified = Column(Boolean, default=False)
    phone_verify = Column(Boolean, default=False)
    email_verify = Column(Boolean, default=False)

    phone_expire_at = Column(DateTime, nullable=True)

    phone_otp = Column(Integer, nullable=True, default=23456)
    email_otp = Column(Integer, nullable=True, default=123456)

    is_profile_complete = Column(Boolean, default=False)
    description = Column(String, nullable=True)

    is_active = Column(Boolean, default=False)

    user_type = Column(Enum(userType), default=userType.user, nullable=True)

    image = Column(String, nullable=True)

    dob = Column(DateTime, nullable=True)

    refresh_token = Column(String, nullable=True)