from app.services.password_service import PasswordService
from app.services.session_service import SessionService, SessionTokenService, get_session_service
from app.services.user_service import UserService, get_user_service
from app.schemas.adminSchemas import createAdmin

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette import status
from fastapi import Depends, Request

from app.middleware.auth_middleware import jwt_auth_admin
from app.utils.enum import userType


# -----------------------------
# CREATE ADMIN
# -----------------------------
async def create(
    data: createAdmin,
    user_service: UserService = Depends(get_user_service)
):
    try:
        payload = jsonable_encoder(data)

        payload["password"] = await PasswordService.create_password(payload["password"])
        payload["user_type"] = userType.admin

        resData = await user_service.create_user(payload)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=resData
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


# -----------------------------
# LOGIN
# -----------------------------
async def login(
    data: createAdmin,
    user_service: UserService = Depends(get_user_service),
    session_service: SessionService = Depends(get_session_service)
):
    try:
        payload = jsonable_encoder(data)

        #  Find user
        admin = await user_service.get_user_by_email(payload["email"])

        if admin is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Admin not found"}
            )

        #  Verify password
        passwordValid = await  PasswordService.verify_password(
            payload["password"],
            admin["password"]
        )

        if not passwordValid:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Wrong credentials"}
            )

        #  Create token (STATIC)
        tokenPayload = {
            "user_id": admin["id"]
        }

        token = SessionTokenService.create_session(tokenPayload)

        # Save session (DI)
        sessionData = {
            "user_id": admin["id"],
            "email": admin["email"],
            "user_type": userType.admin,
            "access_token": token,
            "device_id": "android",
            "device_token": "xva98hjd82gd892v8dnjs8ub37vdu2ug8y93hd8",
            "device_type_id": "abc12345"
        }

        await session_service.create_session_data(sessionData)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "login successful",
                "token": token,
                "status": 200
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


# -----------------------------
# EDIT PROFILE
# -----------------------------
async def editProfile(
    data: dict,
    admin=Depends(jwt_auth_admin),
    user_service: UserService = Depends(get_user_service)
):
    try:
        payload = jsonable_encoder(data)

        updateData = {
            "first_name": payload["first_name"],
            "last_name": payload["last_name"]
        }

        adminData = await user_service.find_by_id_update(
            admin.get("id"),
            updateData
        )

        return JSONResponse(content={
            "message": "Profile updated successfully",
            "data": adminData,
            "status": 200
        })

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )


# -----------------------------
# LOGOUT
# -----------------------------
async def logout(
    request: Request,
    admin=Depends(jwt_auth_admin),
    session_service: SessionService = Depends(get_session_service)
):
    try:
        token = request.headers.get("Authorization")
        exact_token = token.split(" ")[1]

        await session_service.delete_session(exact_token)

        return JSONResponse(
            content={
                "message": "logout successfully",
                "status": 200
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )