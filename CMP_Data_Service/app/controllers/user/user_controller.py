from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from datetime import datetime, timedelta

from core.database import get_db
from app.middleware.auth_middleware import jwt_auth
from app.services.session_service import SessionService
from app.services.user_service import UserService
from app.schemas.user_schema import SignupValidation, VerifyOtps, editProfileSchema, ResentOtp
from app.utils.enum import userType
from app.utils.constants import generateOtp


# -----------------------------
# CREATE USER (SIGNUP)
# -----------------------------
async def create_user(data: SignupValidation, db: AsyncSession = Depends(get_db)):
    try:
        payload = jsonable_encoder(data)

        user = await UserService.find_by_number(db, payload["phone_number"])
        otp = generateOtp()

        if not user:
            payload1 = {
                "phone_expire_at": datetime.now() + timedelta(minutes=2),
                "phone_otp": otp,
                "phone_number": payload["phone_number"],
                "country_code": payload["country_code"],
                "user_type": userType.user
            }

            userData = await UserService.create_user(db, payload1)

            return JSONResponse(content={
                "message": "created",
                "data": {"otp": otp, "user": userData, "expireIn": "2 min"},
                "status": 201
            }, status_code=201)

        if user["is_phone_verified"]:
            return JSONResponse(
                content={"message": "User already exists"},
                status_code=400
            )

        payload1 = {
            "phone_expire_at": datetime.now() + timedelta(minutes=2),
            "phone_otp": otp
        }

        userData = await UserService.find_by_id_update(db, user["id"], payload1)

        return JSONResponse(content={
            "message": "updated",
            "data": {"otp": otp, "user": userData, "expireIn": "2 min"},
            "status": 200
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


# -----------------------------
# LOGIN (SEND OTP)
# -----------------------------
async def login(data: SignupValidation, db: AsyncSession = Depends(get_db)):
    try:
        payload = jsonable_encoder(data)

        user = await UserService.get_user(db, payload["phone_number"])

        if not user:
            return JSONResponse(content={"message": "User not exist"}, status_code=400)

        if user.get("is_blocked"):
            return JSONResponse(content={"message": "User blocked"}, status_code=403)

        otp = generateOtp()

        update = {
            "phone_expire_at": datetime.now() + timedelta(minutes=2),
            "phone_otp": otp,
            "is_phone_otp_verified": False
        }

        await UserService.find_by_id_update(db, user["id"], update)

        return JSONResponse(content={
            "message": "Otp sent successfully",
            "otp": otp,
            "status": 200
        })

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# -----------------------------
# VERIFY OTP
# -----------------------------
async def verifyOtp(data: VerifyOtps, db: AsyncSession = Depends(get_db)):
    try:
        payload = jsonable_encoder(data)

        user = await UserService.find_by_id(db, payload["user_id"])

        if not user:
            return JSONResponse(content={"message": "User not found"}, status_code=404)

        expire_time = user["phone_expire_at"]
        if isinstance(expire_time, str):
            expire_time = datetime.fromisoformat(expire_time)

        if expire_time <= datetime.now():
            return JSONResponse(content={"message": "Otp expired"}, status_code=403)

        if user["phone_otp"] != payload["otp"]:
            return JSONResponse(content={"message": "Invalid OTP"}, status_code=400)

        update = {
            "is_active": True,
            "is_phone_otp_verified": True,
            "phone_verify": True
        }

        tokenPayload = {"user_id": user["id"]}
        token = SessionService.create_session(tokenPayload)
        refreshToken = SessionService.create_refresh_session(tokenPayload)

        sessionData = {
            "user_id": user["id"],
            "phone_number": user["phone_number"],
            "user_type": userType.user,
            "access_token": token,
            "device_id": "android"
        }

        await SessionService.create_session_data(db, sessionData)

        update["refresh_token"] = refreshToken

        updatedUser = await UserService.find_by_id_update(db, user["id"], update)

        updatedUser["access_token"] = token
        updatedUser["refresh_token"] = refreshToken

        return JSONResponse(content=updatedUser, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# -----------------------------
# EDIT PROFILE
# -----------------------------
async def editProfile(
    data: editProfileSchema,
    currentUser=Depends(jwt_auth),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jsonable_encoder(data)

        update = payload

        userData = await UserService.find_by_id_update(
            db,
            currentUser["id"],
            update
        )

        return JSONResponse(content={
            "message": "success",
            "data": userData,
            "status": 200
        })

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# -----------------------------
# RESEND OTP
# -----------------------------
async def resentOtp(data: ResentOtp, db: AsyncSession = Depends(get_db)):
    try:
        payload = jsonable_encoder(data)

        user = await UserService.find_by_id(db, payload.get("user_id"))
        otp = generateOtp()

        if payload.get("type") == "email":
            update = {
                "email_expire_at": datetime.now() + timedelta(minutes=2),
                "email_otp": otp,
                "is_email_otp_verified": False
            }

        elif payload.get("type") == "phone":
            update = {
                "phone_expire_at": datetime.now() + timedelta(minutes=2),
                "phone_otp": otp,
                "is_phone_otp_verified": False
            }
        else:
            return JSONResponse(content={"message": "Bad request"}, status_code=400)

        await UserService.find_by_id_update(db, user["id"], update)

        return JSONResponse(content={
            "otp": otp,
            "status": 200
        })

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# -----------------------------
# LOGOUT
# -----------------------------
async def logout(currentUser=Depends(jwt_auth), db: AsyncSession = Depends(get_db)):
    try:
        await SessionService.delete_session_by_user_id(db, currentUser["id"])

        return JSONResponse(content={
            "message": "Logout successful",
            "status": 200
        })

    except Exception:
        return JSONResponse(content={"message": "Server error"}, status_code=500)


# -----------------------------
# DELETE ACCOUNT
# -----------------------------
async def deleteAccount(currentUser=Depends(jwt_auth), db: AsyncSession = Depends(get_db)):
    try:
        await UserService.find_by_id_update(
            db,
            currentUser["id"],
            {"is_deleted": True}
        )

        await SessionService.delete_session_by_user_id(db, currentUser["id"])

        return JSONResponse(content={
            "message": "Account deleted",
            "status": 200
        })

    except Exception:
        return JSONResponse(content={"message": "Server error"}, status_code=500)