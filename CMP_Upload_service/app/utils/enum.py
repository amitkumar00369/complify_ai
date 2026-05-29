
from enum import Enum


class userType(str, Enum):
    user="user"
    admin="admin"


    
    
class cmsType(str,Enum):
    aboutUs = "aboutUs"
    privacyPolicy = "privacyPolicy"
    termsAndConditions = "termsAndConditions"
    contactUse = "contactUs"

class allowedModules(str,Enum):
    saber = "saber"
    saleem = "saleem"
    standards = "standards"
    technical_regulation = "technical-regulation"
    saber_cases = "saber-cases"
    hs_code = "hs-code"
class allowedExtensions(str,Enum):
    zip = ".zip"
    pdf = ".pdf"
    doc = ".doc"
    docx = ".docx"
    xlsx = ".xlsx"
    xls = ".xls"
    csv = ".csv"
    png = ".png"
    jpg = ".jpg"
    jpeg = ".jpeg"


class subFolderModule(str,Enum):
    raw = "raw"
    processing = "processing"
    processed = "processed"
    archived = "archived"
    failed = "failed"
    


    
class paymentStatus(str,Enum):
    pending = "0"
    completed = "1"
    failed = "2"


class paymentMethod(str,Enum):
    card = "0"
    upi = "1"
    netbanking = "2"
    
    


    



    
    
    