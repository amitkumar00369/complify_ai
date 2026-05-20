from app.controllers.compliance.products import upload_case,getList,getDetailsById
from app.controllers.compliance.STD import upload_std
from app.controllers.compliance.TR import upload_tr,get_tr, createToc
from app.controllers.compliance.KSA import upload_ksa
from app.controllers.compliance.saber import upload_saber
from app.controllers.compliance.TR_Req import createRequirement

from fastapi import APIRouter
from app.controllers.compliance.hs_code_controller import (importHSMaster,getHSCodeDetail,searchHSCode,testAPI)
complianceRouter: APIRouter = APIRouter()

complianceRouter.post("/hs-code/import")(importHSMaster)
complianceRouter.get("/hs-code/search")(searchHSCode)
complianceRouter.get("/hs-code/{hs_code}")(getHSCodeDetail)

complianceRouter.post("/upload-item")(upload_case)
complianceRouter.post("/upload-tr")(upload_tr)
complianceRouter.post("/upload-std")(upload_std)
complianceRouter.post("/upload-ksa-saleem")(upload_ksa)
complianceRouter.post("/upload-saber")(upload_saber)
complianceRouter.get("/get-products")(getList)
complianceRouter.get("/get-product-details/{product_id}")(getDetailsById)

complianceRouter.get("/get-tr")(get_tr)
complianceRouter.post("/create-tr-toc")(createToc)
complianceRouter.post("/create-tr-req")(createRequirement)




