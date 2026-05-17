from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.standard import Standard


# =========================
# STANDARD SERVICE
# =========================
class StandardService:

    def __init__(self, db: AsyncSession):
        self.db = db

   
# GET ALL
# =========================
    async def get_all(self, find=None):
        try:
            

            stmt = (
                select(Standard)
                .where(
                    Standard.is_deleted == False
                )
                .order_by(
                    desc(Standard.created_at)
                )
            )

            # dynamic filters
            if find:
                stmt = stmt.filter_by(**find)

            result = await self.db.execute(stmt)

            standards = result.scalars().all()

            return jsonable_encoder(standards)
        except Exception as e:
            print(str(e))
            return {}
    async def find_by_id(self, standard_id: int):
        try:

            stmt = select(Standard).where(
                Standard.id == standard_id,
                Standard.is_deleted == False
            )

            result = await self.db.execute(stmt)

            standard = result.scalar_one_or_none()

            if not standard:
                return None

            return jsonable_encoder(standard)

        except Exception as e:
            print(str(e))
            return None


# =========================
# DEPENDENCY INJECTION
# =========================
def get_standard_service(
    db: AsyncSession = Depends(get_db)
):

    return StandardService(db)