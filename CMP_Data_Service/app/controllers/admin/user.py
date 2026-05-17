from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database import get_db
from app.middleware.auth_middleware import jwt_auth_admin
from app.services.user_service import UserService


# -----------------------------
# GET USER LIST
# -----------------------------
async def getUserList(
    request: Request,
    admin=Depends(jwt_auth_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = {
            "page": int(request.query_params.get("page", 1)),
            "limit": int(request.query_params.get("limit", 10))
        }

        users = await UserService.get_list(db, option=query)

        return JSONResponse(
            content={
                "message": "user list",
                "data": users,
                "status": 200
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal server error",
                "err": str(e),
                "status": 500
            },
            status_code=500
        )


# -----------------------------
# BLOCK / UNBLOCK USER
# -----------------------------
async def blockUnblocked(
    id: int,
    admin=Depends(jwt_auth_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await UserService.find_by_id(db, id)

        if not user:
            return JSONResponse(
                content={"message": "User not found", "status": 404},
                status_code=404
            )

        if user.get("is_blocked"):
            await UserService.find_by_id_update(db, id, {"is_blocked": False})
            message = "User has been unblocked"
        else:
            await UserService.find_by_id_update(db, id, {"is_blocked": True})
            message = "User has been blocked"

        return JSONResponse(
            content={"message": message, "status": 200}
        )

    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal server error",
                "err": str(e),
                "status": 500
            },
            status_code=500
        )


# -----------------------------
# DELETE USER (SOFT DELETE)
# -----------------------------
async def deleteUser(
    id: int,
    admin=Depends(jwt_auth_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await UserService.find_by_id(db, id)

        if not user:
            return JSONResponse(
                content={"message": "User not found", "status": 404},
                status_code=404
            )

        await UserService.find_by_id_update(db, id, {"is_deleted": True})

        return JSONResponse(
            content={
                "message": "user deleted successfully",
                "status": 200
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "message": "Internal server error",
                "err": str(e),
                "status": 500
            },
            status_code=500
        )