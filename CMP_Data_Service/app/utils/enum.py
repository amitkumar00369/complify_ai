
from enum import Enum


class userType(str, Enum):
    user="user"
    admin="admin"


    
    
class cmsType(str,Enum):
    aboutUs = "aboutUs"
    privacyPolicy = "privacyPolicy"
    termsAndConditions = "termsAndConditions"
    contactUse = "contactUs"

class moduleType(str,Enum):
    saber = "saber"
    saleem = "saleem"
    standards = "standards"
    technicalRegulation = "technical-regulation"
    item = "item"
    


    
class paymentStatus(str,Enum):
    pending = "0"
    completed = "1"
    failed = "2"


class paymentMethod(str,Enum):
    card = "0"
    upi = "1"
    netbanking = "2"
    
class periodType(str,Enum):
    default = "0"  #24 hours plan will active
    monthly = "1"      # for one month  
    quaterly = "2"      # for three month
    yearly = "3"   # for one year
    
class planStatus(str,Enum):
    active = "0"
    expired = "1"
    
class planType(str,Enum):
    free = "0"
    paid = "1"
    
class bussinesType(str,Enum):
    it_services = "0"
    healthcare = "1"
    education = "2"
    finance = "3"
    retail = "4"
    real_estate = "5"
    hospitality = "6"
    manufacturing = "7"
    transportation = "8"
    entertainment = "9"
    restaurants = "10"
    salon="11"
    