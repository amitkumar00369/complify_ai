# =========================================================
# FILE: app/controllers/query_controller.py
# =========================================================

from fastapi import Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from app.utils.arbic_char import SmartTranslator
from app.services.query_service import QueryService


async def query(
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):

    try:

        user_query = data.get("query")

        print(
            f"Received query: {user_query}"
        )

        if not user_query:

            return JSONResponse(
                content={
                    "success": False,
                    "message": "Query is required"
                },
                status_code=400
            )

        # =========================
        # TRANSLATE
        # =========================

        query_in_english = SmartTranslator.smart_translate(
                user_query
            )
        

        print(
            "query_in_english",
            query_in_english
        )

        # =========================
        # QUERY SERVICE
        # =========================

        query_service = QueryService(db)

        result = await query_service.process_query(
                query_in_english
            )
    

        return JSONResponse(
            content={
                "success": True,
                "message": (
                    "Query processed "
                    "successfully"
                ),
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