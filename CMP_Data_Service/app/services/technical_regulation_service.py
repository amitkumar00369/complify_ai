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

    # =====================================
    # CREATE
    # =====================================
    async def create_technical_regulation(
        self,
        data: dict
    ):

        try:

            new_record = Technical_regulation(**data)

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
        tr_id: int
    ):

        stmt = select(Technical_regulation).where(
            Technical_regulation.id == tr_id,
            Technical_regulation.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        return jsonable_encoder(technical_regulation)

    # =====================================
    # GET BY TECHNICAL REGULATION ID
    # =====================================
    async def get_by_tr_id(
        self,
        technical_regulation_id: str
    ):

        stmt = select(Technical_regulation).where(
            Technical_regulation.tr_id == technical_regulation_id,
            Technical_regulation.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        return jsonable_encoder(technical_regulation)
    
    
    #=====================================
    # create_ksa_saleem_in_bulk
    
    # ====================================
    
    async def create_tr_in_bulk(
    self,
    records: list
     ):

        try:
            print(
                f"Attempting to insert {len(records)} TR records in bulk"
            )

            # ==============================
            # GET ALL TR NAMES FROM INPUT
            # ==============================
            tr_names = [
                record["tr_name"]
                for record in records
                if record.get("tr_name")
            ]

            # ==============================
            # CHECK ALREADY EXISTING RECORDS
            # ==============================
            stmt = select(
                Technical_regulation.tr_name
            ).where(
                Technical_regulation.tr_name.in_(tr_names),
                Technical_regulation.is_deleted == False
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
                if record.get("tr_name") not in existing_names
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
                Technical_regulation(**record)
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

    # =====================================
    # GET BY NAME
    # =====================================
    async def get_by_tr_name(
        self,
        tr_name: str
    ):

        stmt = select(Technical_regulation).where(
            Technical_regulation.tr_name == tr_name,
            Technical_regulation.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulations = result.scalars().all()

        return jsonable_encoder(technical_regulations)
    async def find_by_name(
        self,
        name: str
    ):

        stmt = select(Technical_regulation).where(
            Technical_regulation.tr_name == name,
            Technical_regulation.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        return jsonable_encoder(technical_regulation)

    # =====================================
    # UPDATE
    # =====================================
    async def find_by_id_update(
        self,
        tr_id: int,
        payload: dict
    ):

        stmt = select(Technical_regulation).where(
            Technical_regulation.id == tr_id,
            Technical_regulation.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        if not technical_regulation:
            return None

        for key, value in payload.items():

            setattr(technical_regulation, key, value)

        await self.db.commit()

        await self.db.refresh(technical_regulation)

        return jsonable_encoder(technical_regulation)

    # =====================================
    # DELETE (SOFT DELETE)
    # =====================================
    async def delete_technical_regulation(
        self,
        tr_id: int
    ):

        stmt = select(Technical_regulation).where(
            Technical_regulation.id == tr_id,
            Technical_regulation.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        if not technical_regulation:
            return None

        technical_regulation.is_deleted = True

        await self.db.commit()

        return {
            "message": "Technical Regulation deleted successfully"
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
            select(Technical_regulation)
            .where(
                Technical_regulation.is_deleted == False
            )
            .order_by(
                desc(Technical_regulation.created_at)
            )
        )

        result = await self.db.execute(stmt)

        technical_regulations = result.scalars().all()

        data = jsonable_encoder(technical_regulations)

        return PaginationRsponse.returnData(
            data,
            option
        )
    
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


# =====================================
# DEPENDENCY INJECTION
# =====================================
def get_technical_regulation_service(
    db: AsyncSession = Depends(get_db)
):

    return TechnicalRegulationService(db)