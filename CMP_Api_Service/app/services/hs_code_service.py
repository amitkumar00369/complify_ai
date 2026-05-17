import os
import shutil

from fastapi import UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from fastapi.encoders import jsonable_encoder

from core.database import get_db
from app.models.hs_master import HSMaster


class HSCodeService:

    def __init__(
        self,
        db: AsyncSession
    ):

        self.db = db

    async def get_all(
        self,
        find=None
    ):

        try:

            stmt = (
                select(HSMaster)
                .where(
                    HSMaster.is_deleted == False
                )
                .order_by(
                    desc(HSMaster.created_at)
                )
            )

            if find:

                stmt = stmt.filter_by(**find)

            result = await self.db.execute(stmt)

            hscodes = result.scalars().all()

            return jsonable_encoder(hscodes)

        except Exception as e:

            print(str(e))

            return {}
    async def find_by_id(self, hs_code):
        try:

            stmt = select(HSMaster).where(
                HSMaster.full_hs_code == hs_code,
                HSMaster.is_deleted == False
            )

            result = await self.db.execute(stmt)

            standard = result.scalar_one_or_none()

            if not standard:
                return None

            return jsonable_encoder(standard)

        except Exception as e:
            print(str(e))
            return None
def get_hs_code_service(
    db: AsyncSession = Depends(get_db)
):

    return HSCodeService(db)