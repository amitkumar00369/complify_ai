from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from fastapi import Depends
import jwt 

from core.config import settings
from core.database import get_db
from app.models.session_model import Session


# =========================
#  TOKEN SERVICE (STATIC)
# =========================
class SessionTokenService:

    @staticmethod
    def create_session(payload: dict):
        payload["exp"] = datetime.utcnow() + timedelta(hours=24)
        payload["iat"] = datetime.utcnow()
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_session(payload: dict):
        payload["exp"] = datetime.utcnow() + timedelta(days=30)
        payload["iat"] = datetime.utcnow()
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_session(token: str):
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")


# =========================
#  SESSION DB SERVICE (DI)
# =========================
class SessionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session_data(self, payload: dict):
        try:
            new_record = Session(**payload)
            self.db.add(new_record)

            await self.db.commit()
            await self.db.refresh(new_record)

            return jsonable_encoder(new_record)

        except Exception:
            await self.db.rollback()
            raise

    async def delete_session(self, token: str):
        stmt = select(Session).where(Session.access_token == token)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            await self.db.delete(session)
            await self.db.commit()
            return True

        return False

    async def delete_session_by_user_id(self, user_id: int):
        stmt = delete(Session).where(Session.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def get_all_session_data(self):
        stmt = select(Session).order_by(Session.id.desc())
        result = await self.db.execute(stmt)

        sessions = result.scalars().all()
        return jsonable_encoder(sessions)

    async def get_session_data(self, token: str):
        stmt = select(Session).where(Session.access_token == token)
        result = await self.db.execute(stmt)

        session = result.scalar_one_or_none()
        return jsonable_encoder(session)


# =========================
# 🔌 DEPENDENCY INJECTION
# =========================
def get_session_service(db: AsyncSession = Depends(get_db)):
    return SessionService(db)