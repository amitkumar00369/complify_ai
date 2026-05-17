from fastapi import Request, HTTPException, Depends

from app.utils.enum import userType
from app.services.session_service import (
    SessionService,
    SessionTokenService,
    get_session_service
)
from app.services.user_service import UserService, get_user_service


# =========================
# USER AUTH
# =========================
async def jwt_auth(
    request: Request,
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service)
):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Bearer token format")

    exact_token = token.split(" ")[1]

    #  Check session in DB (ASYNC)
    session = await session_service.get_session_data(exact_token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    #  Decode token (STATIC)
    try:
        user_id = SessionTokenService.decode_session(exact_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    #  Fetch user (ASYNC)
    user = await user_service.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_deleted"):
        raise HTTPException(status_code=403, detail="User deleted")

    if user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="User blocked")

    request.state.user = user
    return user


# =========================
# ADMIN AUTH
# =========================
async def jwt_auth_admin(
    request: Request,
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service)
):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Bearer token format")

    exact_token = token.split(" ")[1]

    #  Check session
    session = await session_service.get_session_data(exact_token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    #  Decode token
    try:
        user_id = SessionTokenService.decode_session(exact_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    #  Fetch user
    user = await user_service.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_deleted"):
        raise HTTPException(status_code=403, detail="User deleted")

    if user.get("is_blocked"):
        raise HTTPException(status_code=403, detail="User blocked")

    #  Admin check
    if user.get("user_type") != userType.admin:
        raise HTTPException(status_code=403, detail="Access denied")

    request.state.user = user
    return user