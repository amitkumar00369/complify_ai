# =========================================================
# FILE: app/controllers/query_controller.py
# =========================================================

from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool

from app.services.query_service import QueryService
from app.utils.arbicChar import SmartTranslator


async def process_query(data: dict):

    try:

        user_query = data.get("query")
        print(f"Received query: {user_query}")
        

        if not user_query:

            return JSONResponse(
                content={
                    "success": False,
                    "message": "Query is required"
                },
                status_code=400
            )
        queryInEng = SmartTranslator.smart_translate(user_query)
        print("english query",queryInEng)

        result = await QueryService.process_query(user_query)
        

        return JSONResponse(
            content={
                "success": True,
                "message": "Query processed successfully",
                "data": result
            },
            status_code=200
        )

    except Exception as e:

        return JSONResponse(
            content={
                "success": False,
                "message": str(e)
            },
            status_code=500
        )