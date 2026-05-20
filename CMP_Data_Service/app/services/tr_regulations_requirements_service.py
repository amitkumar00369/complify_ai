from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.technical_regulations import Technical_regulation
from app.models.Technical_regulations_requirements_model import TR_REQUIREMENTS



# =====================================
# TECHNICAL REGULATION SERVICE
# =====================================
class TR_REQUIREMENTS_Service:

    def __init__(self, db: AsyncSession):
        self.db = db

    # =====================================
    # CREATE
    # =====================================
    async def create_tr_requirements(
        self,
        data: dict
    ):

        try:

            new_record = TR_REQUIREMENTS(**data)

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

        stmt = select(TR_REQUIREMENTS).where(
            TR_REQUIREMENTS.id == tr_id,
            TR_REQUIREMENTS.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        return jsonable_encoder(technical_regulation)

    # =====================================
    # GET BY TECHNICAL REGULATION ID
    # =====================================
    async def get_by_tr_req_id(
        self,
        technical_regulation_id: str
    ):

        stmt = select(TR_REQUIREMENTS).where(
            TR_REQUIREMENTS.tr_id == technical_regulation_id,
            TR_REQUIREMENTS.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulation = result.scalar_one_or_none()

        return jsonable_encoder(technical_regulation)
    
    
    #=====================================
    # create_ksa_saleem_in_bulk
    
    # ====================================
    
    async def create_tr_req_in_bulk(
    self,
    records: list
     ):

        try:

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
                TR_REQUIREMENTS.tr_name
            ).where(
                TR_REQUIREMENTS.tr_name.in_(tr_names),
                TR_REQUIREMENTS.is_deleted == False
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
                TR_REQUIREMENTS(**record)
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
    async def get_by_tr_req_name(
        self,
        tr_name: str
    ):

        stmt = select(TR_REQUIREMENTS).where(
            TR_REQUIREMENTS.tr_name == tr_name,
            TR_REQUIREMENTS.is_deleted == False
        )

        result = await self.db.execute(stmt)

        technical_regulations = result.scalars().all()

        return jsonable_encoder(technical_regulations)

    # =====================================
    # UPDATE
    # =====================================
    async def find_by_id_update(
        self,
        tr_id: int,
        payload: dict
    ):

        stmt = select(TR_REQUIREMENTS).where(
            TR_REQUIREMENTS.id == tr_id,
            TR_REQUIREMENTS.is_deleted == False
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
    async def delete_technical_regulation_req(
        self,
        tr_id: int
    ):

        stmt = select(TR_REQUIREMENTS).where(
            TR_REQUIREMENTS.id == tr_id,
            TR_REQUIREMENTS.is_deleted == False
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
            select(TR_REQUIREMENTS)
            .where(
                TR_REQUIREMENTS.is_deleted == False
            )
            .order_by(
                desc(TR_REQUIREMENTS.created_at)
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
                select(TR_REQUIREMENTS)
                .where(
                    TR_REQUIREMENTS.is_deleted == False
                )
                .order_by(
                    desc(TR_REQUIREMENTS.created_at)
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
def get_tr_requirements_service(
    db: AsyncSession = Depends(get_db)
):

    return TR_REQUIREMENTS_Service(db)