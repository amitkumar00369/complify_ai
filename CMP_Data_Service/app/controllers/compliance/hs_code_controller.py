from fastapi import Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from app.services.hs_code_service import HSCodeService
from fastapi.encoders import jsonable_encoder
#from app.services.llama_service import databyhscode_usingllm




# -----------------------------
# IMPORT HS MASTER
# -----------------------------
async def importHSMaster(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await HSCodeService.import_hs_master(db, file)
    # return {"yesssssssssss":"haaaaaaaaaaaaaaaaaa"}



# -----------------------------
# GET HS DETAIL
# -----------------------------
async def getHSCodeDetail(
    hs_code: str,
    db: AsyncSession = Depends(get_db)
):
    result = await HSCodeService.get_hs_code_detail(db, hs_code)
    #print("HS Code",result)

    if not result:
        raise HTTPException(status_code=404, detail="HS code not found")

    return result


# -----------------------------
# SEARCH HS
# -----------------------------
async def searchHSCode(
    keyword: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    return await HSCodeService.search_hs_codes(db, keyword)

# -----------------------------
# MAtch Hashcode im the minstral model
# -----------------------------

async def testAPI(data:dict):
    payload=jsonable_encoder(data)
    #result=databyhscode_usingllm(payload.get("hs_code","40210120002"))
    return {
        "result": payload
    }
