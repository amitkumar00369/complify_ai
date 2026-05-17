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

    # =========================
    # CREATE
    # =========================
    async def create_standard(self, data: dict):

        try:

            new_record = Standard(**data)

            self.db.add(new_record)

            await self.db.commit()

            await self.db.refresh(new_record)

            return jsonable_encoder(new_record)

        except Exception:

            await self.db.rollback()

            raise

    # =========================
    # GET BY ID
    # =========================
    async def find_by_id(self, standard_id: int):

        stmt = select(Standard).where(
            Standard.id == standard_id,
            Standard.is_deleted == False
        )

        result = await self.db.execute(stmt)

        standard = result.scalar_one_or_none()

        return jsonable_encoder(standard)
    
    # ========================================================
    # create_ksa_saleem_in_bulk
    # =====================================
    async def create_standard_in_bulk(self,records: list):
        try:

            # ==============================
            # GET ALL KSA NAMES FROM INPUT
            # ==============================
            std_names = [
                record["std_name"]
                for record in records
                if record.get("std_name")
            ]

            # ==============================
            # CHECK ALREADY EXISTING RECORDS
            # ==============================
            stmt = select(
                Standard.std_name
            ).where(
                Standard.std_name.in_(std_names),
                Standard.is_deleted == False
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
                if record.get("std_name") not in existing_names
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
                Standard(**record)
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
    # GET BY STANDARD ID
    # =========================
    async def get_by_standard_id(
        self,
        standard_unique_id: str
    ):

        stmt = select(Standard).where(
            Standard.standard_id == standard_unique_id,
            Standard.is_deleted == False
        )

        result = await self.db.execute(stmt)

        standard = result.scalar_one_or_none()

        return jsonable_encoder(standard)

    # =========================
    # GET BY STANDARD NAME
    # =========================
    async def get_by_standard_name(
        self,
        std_name: str
    ):

        stmt = select(Standard).where(
            Standard.std_name == std_name,
            Standard.is_deleted == False
        )

        result = await self.db.execute(stmt)

        standards = result.scalars().all()

        return jsonable_encoder(standards)

    # =========================
    # UPDATE
    # =========================
    async def find_by_id_update(
        self,
        standard_id: int,
        payload: dict
    ):

        stmt = select(Standard).where(
            Standard.id == standard_id,
            Standard.is_deleted == False
        )

        result = await self.db.execute(stmt)

        standard = result.scalar_one_or_none()

        if not standard:
            return None

        for key, value in payload.items():

            setattr(standard, key, value)

        await self.db.commit()

        await self.db.refresh(standard)

        return jsonable_encoder(standard)

    # =========================
    # DELETE (SOFT DELETE)
    # =========================
    async def delete_standard(
        self,
        standard_id: int
    ):

        stmt = select(Standard).where(
            Standard.id == standard_id,
            Standard.is_deleted == False
        )

        result = await self.db.execute(stmt)

        standard = result.scalar_one_or_none()

        if not standard:
            return None

        standard.is_deleted = True

        await self.db.commit()

        return {
            "message": "Standard deleted successfully"
        }

    # =========================
    # LIST STANDARDS
    # =========================
    async def get_list(
        self,
        find=None,
        option={"page": 1, "limit": 10}
    ):

        stmt = (
            select(Standard)
            .where(
                Standard.is_deleted == False
            )
            .order_by(
                desc(Standard.created_at)
            )
        )

        result = await self.db.execute(stmt)

        standards = result.scalars().all()

        data = jsonable_encoder(standards)

        return PaginationRsponse.returnData(
            data,
            option
        )
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


# =========================
# DEPENDENCY INJECTION
# =========================
def get_standard_service(
    db: AsyncSession = Depends(get_db)
):

    return StandardService(db)