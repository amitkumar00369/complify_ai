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

    # =========================
    # CREATE
    # =========================
    async def create_saber(self, data: dict):

        try:

            new_record = Saber(**data)

            self.db.add(new_record)

            await self.db.commit()

            await self.db.refresh(new_record)

            return jsonable_encoder(new_record)

        except Exception:

            await self.db.rollback()

            raise
        
    #=============bulk created ====================
    async def create_saber_in_bulk(self,records: list):
        try:

            # ==============================
            # GET ALL KSA NAMES FROM INPUT
            # ==============================
            saber_names = [
                record["saber_name"]
                for record in records
                if record.get("saber_name")
            ]

            # ==============================
            # CHECK ALREADY EXISTING RECORDS
            # ==============================
            stmt = select(
                Saber.saber_name
            ).where(
                Saber.saber_name.in_(saber_names),
                Saber.is_deleted == False
            )

            result = await self.db.execute(stmt)

            existing_names = set(
                result.scalars().all()
            )

            # ==============================
            # FILTER NEW RECORDS ONLY
            # ==============================
            new_records_data = [
                record
                for record in records
                if record.get("saber_name") not in existing_names
            ]

            # ==============================
            # IF ALL RECORDS ALREADY EXIST
            # ==============================
            if not new_records_data:

                return {
                    "message": "All records already exist",
                    "inserted_count": 0,
                    "data": []
                }

            # ==============================
            # CREATE MODEL OBJECTS
            # ==============================
            new_records = [
                Saber(**record)
                for record in new_records_data
            ]

            # ==============================
            # INSERT DATA
            # ==============================
            self.db.add_all(new_records)

            await self.db.commit()

            # ==============================
            # REFRESH RECORDS
            # ==============================
            for record in new_records:
                await self.db.refresh(record)

            return {
                "message": "Bulk records inserted successfully",
                "inserted_count": len(new_records),
                "skipped_count": len(existing_names),
                "data": jsonable_encoder(new_records)
            }

        except Exception as e:

            await self.db.rollback()

            print(str(e))

            raise e

    # =========================
    # GET BY ID
    # =========================
    async def find_by_id(self, saber_id: int):

        stmt = select(Saber).where(
            Saber.id == saber_id,
            Saber.is_deleted == False
        )

        result = await self.db.execute(stmt)

        saber = result.scalar_one_or_none()

        return jsonable_encoder(saber)

    # =========================
    # GET BY SABER ID
    # =========================
    async def get_by_saber_id(
        self,
        saber_unique_id: str
    ):

        stmt = select(Saber).where(
            Saber.saber_id == saber_unique_id,
            Saber.is_deleted == False
        )

        result = await self.db.execute(stmt)

        saber = result.scalar_one_or_none()

        return jsonable_encoder(saber)

    # =========================
    # GET BY SABER NAME
    # =========================
    async def get_by_saber_name(
        self,
        saber_name: str
    ):

        stmt = select(Saber).where(
            Saber.saber_name == saber_name,
            Saber.is_deleted == False
        )

        result = await self.db.execute(stmt)

        sabers = result.scalars().all()

        return jsonable_encoder(sabers)

    # =========================
    # UPDATE
    # =========================
    async def find_by_id_update(
        self,
        saber_id: int,
        payload: dict
    ):

        stmt = select(Saber).where(
            Saber.id == saber_id,
            Saber.is_deleted == False
        )

        result = await self.db.execute(stmt)

        saber = result.scalar_one_or_none()

        if not saber:
            return None

        for key, value in payload.items():

            setattr(saber, key, value)

        await self.db.commit()

        await self.db.refresh(saber)

        return jsonable_encoder(saber)

    # =========================
    # DELETE (SOFT DELETE)
    # =========================
    async def delete_saber(
        self,
        saber_id: int
    ):

        stmt = select(Saber).where(
            Saber.id == saber_id,
            Saber.is_deleted == False
        )

        result = await self.db.execute(stmt)

        saber = result.scalar_one_or_none()

        if not saber:
            return None

        saber.is_deleted = True

        await self.db.commit()

        return {
            "message": "Saber deleted successfully"
        }

    # =========================
    # LIST SABERS
    # =========================
    async def get_list(
        self,
        find=None,
        option={"page": 1, "limit": 10}
    ):

        stmt = (
            select(Saber)
            .where(
                Saber.is_deleted == False
            )
            .order_by(
                desc(Saber.created_at)
            )
        )

        result = await self.db.execute(stmt)

        sabers = result.scalars().all()

        data = jsonable_encoder(sabers)

        return PaginationRsponse.returnData(
            data,
            option
        )


# =========================
# DEPENDENCY INJECTION
# =========================
def get_saber_service(
    db: AsyncSession = Depends(get_db)
):

    return SaberService(db)