from pydantic import BaseModel
from typing import Optional


class HSCodeResponse(BaseModel):
    hs_code: str
    chapter_code: str
    heading_code: str
    subheading_code: str
    item_name_en: Optional[str] = None
    item_name_ar: Optional[str] = None
    duty_rate_en: Optional[str] = None
    duty_rate_ar: Optional[str] = None
    procedure_codes: Optional[str] = None
    effective_date: Optional[str] = None

    class Config:
        from_attributes = True