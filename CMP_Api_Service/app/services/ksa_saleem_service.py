from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.ksa_saleem import KSAsaleem


# =====================================
# KSA SALEEM SERVICE
# =====================================
class KSASaleemService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # =====================================
    # CREATE
    # =====================================
  
    async def get_all(self, find=None):
        try:
            

            stmt = (
                select(KSAsaleem)
                .where(
                    KSAsaleem.is_deleted == False
                )
                .order_by(
                    desc(KSAsaleem.created_at)
                )
            )

            # dynamic filters
            if find:
                stmt = stmt.filter_by(**find)

            result = await self.db.execute(stmt)

            ksas = result.scalars().all()

            return jsonable_encoder(ksas)
        except Exception as e:
            print(str(e))
            return {}



# =====================================
# DEPENDENCY INJECTION
# =====================================
def get_ksa_saleem_service(
    db: AsyncSession = Depends(get_db)
):

    return KSASaleemService(db)