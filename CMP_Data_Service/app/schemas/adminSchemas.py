from pydantic import BaseModel, EmailStr, Field, field_validator
from fastapi.concurrency import run_in_threadpool
from app.services.user_service import UserService
from fastapi.responses import JSONResponse
class createAdmin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=50)
    
class UserBlockSchema(BaseModel):
    id: int

    @field_validator("id")
    def validate_id(cls, v):
        if v <= 0:
            raise ValueError("ID must be positive")
        return v
    
