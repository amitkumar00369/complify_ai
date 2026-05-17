from pydantic import BaseModel, Field
from typing import Optional,Literal

class SignupValidation(BaseModel):
    phone_number: str=Field(..., pattern=r"^\d{7,15}$")
    country_code: Optional[str] = Field(default="+971",pattern=r"^\+\d{1,4}$")
class VerifyOtps(BaseModel):
    type: Literal["email", "phone"]
    userId: int
    otp: int
class ResentOtp(BaseModel):
    type: Literal["email", "phone"]
    userId: int
    

class changePasswordValidation(BaseModel):
    new_password: str
    old_password: str
class changeEmail(BaseModel):
    old_email: str
    new_email: str
    
class editProfileSchema(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = Field(
        default=None,
        pattern=r"^\d{7,15}$"
    )
    country_code: Optional[str] = Field(
        default="+971",
        pattern=r"^\+\d{1,4}$"
    )
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    image: Optional[str] = None
    dob: Optional[str] = None


