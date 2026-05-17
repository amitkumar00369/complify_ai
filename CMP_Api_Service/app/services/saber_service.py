from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.saber_model import Saber


# =========================
# SABER SERVICE
# =========================
class SaberService:

    def __init__(self, db: AsyncSession):
        self.db = db

   
# GET ALL
# =========================
    async def get_all(self, find=None):
        try:
            

            stmt = (
                select(Saber)
                .where(
                    Saber.is_deleted == False
                )
                .order_by(
                    desc(Saber.created_at)
                )
            )

            # dynamic filters
            if find:
                stmt = stmt.filter_by(**find)

            result = await self.db.execute(stmt)

            sabres = result.scalars().all()

            return jsonable_encoder(sabres)
        except Exception as e:
            print(str(e))
            return {}


# =========================
# DEPENDENCY INJECTION
# =========================
def get_saber_service(
    db: AsyncSession = Depends(get_db)
):

    return SaberService(db)