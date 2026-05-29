from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.user_model import User
from app.utils.enum import userType


# =========================
#  USER SERVICE (DI)
# =========================
class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: dict):
        try:
            new_record = User(**data)
            self.db.add(new_record)

            await self.db.commit()
            await self.db.refresh(new_record)

            return jsonable_encoder(new_record)

        except Exception:
            await self.db.rollback()
            raise

    async def get_user(self, phone_number: str):
        stmt = select(User).where(
            User.phone_number == phone_number,
            User.is_deleted == False,
            User.phone_verify == True
        )

        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return jsonable_encoder(user)

    async def get_user_by_email(self, email: str):
        stmt = select(User).where(User.email == email)

        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return jsonable_encoder(user)

    async def find_by_id_update(self, user_id: int, payload: dict):
        stmt = select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )

        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        for key, value in payload.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)

        return jsonable_encoder(user)

    async def find_by_id(self, user_id: int):
        stmt = select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )

        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return jsonable_encoder(user)

    async def find_by_number(self, phone_number: str):
        stmt = select(User).where(
            User.phone_number == phone_number,
            User.is_deleted == False
        )

        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        return jsonable_encoder(user)

    async def get_list(self, find=None, option={"page": 1, "limit": 10}):
        stmt = (
            select(User)
            .where(
                User.is_deleted == False,
                User.user_type != userType.admin
            )
            .order_by(desc(User.created_at))
        )

        result = await self.db.execute(stmt)
        users = result.scalars().all()

        data = jsonable_encoder(users)
        return PaginationRsponse.returnData(data, option)


# =========================
# 🔌 DEPENDENCY INJECTION
# =========================
def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)