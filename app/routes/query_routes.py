from fastapi import APIRouter, Body

from app.controllers.query_controller import process_query

router = APIRouter()

@router.post("/query")
async def query(data: dict = Body(...)):

    return await process_query(data)