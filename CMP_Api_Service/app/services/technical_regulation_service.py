from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.technical_regulations import Technical_regulation


# =====================================
# TECHNICAL REGULATION SERVICE
# =====================================
class TechnicalRegulationService:

    def __init__(self, db: AsyncSession):
        self.db = db

 
    async def get_all(self, find=None):
        try:
            

            stmt = (
                select(Technical_regulation)
                .where(
                    Technical_regulation.is_deleted == False
                )
                .order_by(
                    desc(Technical_regulation.created_at)
                )
            )

            # dynamic filters
            if find:
                stmt = stmt.filter_by(**find)

            result = await self.db.execute(stmt)

            trs = result.scalars().all()

            return jsonable_encoder(trs)
        except Exception as e:
            print(str(e))
            return {}
    async def find_by_id(self, tr_id: int):
        try:

            stmt = select(Technical_regulation).where(
                Technical_regulation.id == tr_id,
                Technical_regulation.is_deleted == False
            )

            result = await self.db.execute(stmt)

            standard = result.scalar_one_or_none()

            if not standard:
                return None

            return jsonable_encoder(standard)

        except Exception as e:
            print(str(e))
            return None



# =====================================
# DEPENDENCY INJECTION
# =====================================
def get_technical_regulation_service(
    db: AsyncSession = Depends(get_db)
):

    return TechnicalRegulationService(db)