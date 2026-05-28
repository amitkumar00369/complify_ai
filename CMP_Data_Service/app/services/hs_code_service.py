import os
import shutil
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi.encoders import jsonable_encoder
from app.models.hs_master import HSMaster
from app.utils.excel_reader import read_hs_excel_from_upload ,split_hs_code,read_hs_excel_from_path


class HSCodeService:

    @staticmethod
    async def import_hs_master(db: AsyncSession, file: UploadFile):
        records = await read_hs_excel_from_path(file)
        print("Checks in record entry ",len(records))
        # return records[:10]
 
        inserted = 0
        updated = 0

        for record in records:
            record["source_file"] = file.filename

            stmt = select(HSMaster).where(
                HSMaster.full_hs_code == record["full_hs_code"]
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                await db.execute(
                    update(HSMaster)
                    .where(HSMaster.full_hs_code == record["full_hs_code"])
                    .values(**record)
                )
                updated += 1
            else:
                db.add(HSMaster(**record))
                inserted += 1

        await db.commit()

        return {
            "message": "HS Master imported successfully",
            "inserted": inserted,
            "updated": updated,
            "total": len(records)
        }
    @staticmethod
    async def import_hs_master_into_table(db: AsyncSession, file):
        records = await read_hs_excel_from_path(file)
        print("Checks in record entry ",len(records))
        # return records[:10]
 
        inserted = 0
        updated = 0

        for record in records:
            record["source_file"] = file.filename

            stmt = select(HSMaster).where(
                HSMaster.full_hs_code == record["full_hs_code"]
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                await db.execute(
                    update(HSMaster)
                    .where(HSMaster.full_hs_code == record["full_hs_code"])
                    .values(**record)
                )
                updated += 1
            else:
                db.add(HSMaster(**record))
                inserted += 1

        await db.commit()

        return {
            "message": "HS Master imported successfully",
            "inserted": inserted,
            "updated": updated,
            "total": len(records)
        }

    @staticmethod
    async def get_hs_code_detail(db: AsyncSession, hs_code: str):
        stmt = select(HSMaster).where(
            HSMaster.full_hs_code == hs_code
        )
        result = await db.execute(stmt)
        hs = result.scalar_one_or_none()
        if not hs:
            return None

        return {
            "hs_code": hs.full_hs_code,
            "chapter_code": hs.chapter_code,
            "heading_code": hs.heading_code,
            "subheading_code": hs.subheading_code,
            "item_name_en": hs.item_name_en,
            "item_name_ar": hs.item_name_ar,
            "duty_rate_en": hs.duty_rate_en,
            "duty_rate_ar": hs.duty_rate_ar,
            "procedure_codes": hs.procedure_codes,
            "effective_date": str(hs.effective_date) if hs.effective_date else None
        }

    @staticmethod
    async def findOneAndUpdate(db: AsyncSession, hs_code, data):
        try:

            create_data = {
                **split_hs_code(hs_code),
                "item_name_ar": "",
                "item_name_en": data.get("product_name"),
                "duty_rate_ar": "",
                "duty_rate_en": "",
                "procedure_codes": "",
                "effective_date": None,
                "source_sheet": "Grid",
                "source_row": 0,
                "product_id": data.get("id"),
                "product_name": data.get("product_name"),
                "tr_id": data.get("tr_id"),
                "tr_name": data.get("tr_name"),
                "std_id": data.get("std_id"),
                "std_name": data.get("std_name")
            }

            update_data = {
                "product_id": data.get("id"),
                "product_name": data.get("product_name"),
                "tr_id": data.get("tr_id"),
                "tr_name": data.get("tr_name"),
                "std_id": data.get("std_id"),
                "std_name": data.get("std_name")
            }

            print("created_data", create_data)

            stmt = select(HSMaster).where(
                HSMaster.full_hs_code == hs_code
            )

            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            # UPDATE
            if existing:

                for key, value in update_data.items():
                    setattr(existing, key, value)

                response_data = existing

            # CREATE
            else:
                new_record = HSMaster(**create_data)

                db.add(new_record)

                response_data = new_record

            await db.commit()

            await db.refresh(response_data)

            return jsonable_encoder(response_data)

        except Exception as e:
            await db.rollback()
            print("ERROR:", str(e))
            return False