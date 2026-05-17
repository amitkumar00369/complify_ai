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
    async def create_ksa_saleem(
        self,
        data: dict
    ):

        try:

            new_record = KSAsaleem(**data)

            self.db.add(new_record)

            await self.db.commit()

            await self.db.refresh(new_record)

            return jsonable_encoder(new_record)

        except Exception:

            await self.db.rollback()

            raise

    # =====================================
    # GET BY ID
    # =====================================
    async def find_by_id(
        self,
        ksa_id: int
    ):

        stmt = select(KSAsaleem).where(
            KSAsaleem.id == ksa_id,
            KSAsaleem.is_deleted == False
        )

        result = await self.db.execute(stmt)

        ksa_saleem = result.scalar_one_or_none()

        return jsonable_encoder(ksa_saleem)

    # =====================================
    # GET BY KSA ID
    # =====================================
    
    #======================================
    # create_ksa_saleem_in_bulk
    #=============================
    async def create_ksa_saleem_in_bulk(
    self,
    records: list
):

        try:

            # ==============================
            # GET ALL KSA NAMES FROM INPUT
            # ==============================
            ksa_names = [
                record["ksa_name"]
                for record in records
                if record.get("ksa_name")
            ]

            # ==============================
            # CHECK ALREADY EXISTING RECORDS
            # ==============================
            stmt = select(
                KSAsaleem.ksa_name
            ).where(
                KSAsaleem.ksa_name.in_(ksa_names),
                KSAsaleem.is_deleted == False
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
                if record.get("ksa_name") not in existing_names
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
                KSAsaleem(**record)
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
    async def get_by_ksa_id(
        self,
        ksa_unique_id: str
    ):

        stmt = select(KSAsaleem).where(
            KSAsaleem.ksa_id == ksa_unique_id,
            KSAsaleem.is_deleted == False
        )

        result = await self.db.execute(stmt)

        ksa_saleem = result.scalar_one_or_none()

        return jsonable_encoder(ksa_saleem)

    # =====================================
    # GET BY KSA NAME
    # =====================================
    async def get_by_ksa_name(
        self,
        ksa_name: str
    ):

        stmt = select(KSAsaleem).where(
            KSAsaleem.ksa_name == ksa_name,
            KSAsaleem.is_deleted == False
        )

        result = await self.db.execute(stmt)

        ksa_saleems = result.scalars().all()

        return jsonable_encoder(ksa_saleems)

    # =====================================
    # UPDATE
    # =====================================
    async def find_by_id_update(
        self,
        ksa_id: int,
        payload: dict
    ):

        stmt = select(KSAsaleem).where(
            KSAsaleem.id == ksa_id,
            KSAsaleem.is_deleted == False
        )

        result = await self.db.execute(stmt)

        ksa_saleem = result.scalar_one_or_none()

        if not ksa_saleem:
            return None

        for key, value in payload.items():

            setattr(ksa_saleem, key, value)

        await self.db.commit()

        await self.db.refresh(ksa_saleem)

        return jsonable_encoder(ksa_saleem)

    # =====================================
    # DELETE (SOFT DELETE)
    # =====================================
    async def delete_ksa_saleem(
        self,
        ksa_id: int
    ):

        stmt = select(KSAsaleem).where(
            KSAsaleem.id == ksa_id,
            KSAsaleem.is_deleted == False
        )

        result = await self.db.execute(stmt)

        ksa_saleem = result.scalar_one_or_none()

        if not ksa_saleem:
            return None

        ksa_saleem.is_deleted = True

        await self.db.commit()

        return {
            "message": "KSA Saleem deleted successfully"
        }

    # =====================================
    # LIST
    # =====================================
    async def get_list(
        self,
        find=None,
        option={"page": 1, "limit": 10}
    ):

        stmt = (
            select(KSAsaleem)
            .where(
                KSAsaleem.is_deleted == False
            )
            .order_by(
                desc(KSAsaleem.created_at)
            )
        )

        result = await self.db.execute(stmt)

        ksa_saleems = result.scalars().all()

        data = jsonable_encoder(ksa_saleems)

        return PaginationRsponse.returnData(
            data,
            option
        )


# =====================================
# DEPENDENCY INJECTION
# =====================================
def get_ksa_saleem_service(
    db: AsyncSession = Depends(get_db)
):

    return KSASaleemService(db)