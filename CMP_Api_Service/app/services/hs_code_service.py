import os
import shutil

from fastapi import UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from fastapi.encoders import jsonable_encoder

from core.database import get_db
from app.models.hs_master import HSMaster
from app.models.products import Product
from app.models.standard import Standard
from app.models.technical_regulations import Technical_regulation
import json




class HSCodeService:

    def __init__(
        self,
        db: AsyncSession
    ):

        self.db = db
    @staticmethod
    async def normalize_text(text):

        if text is None:
            return ""

        text = str(text).lower()

        text = text.replace("-", " ")
        text = text.replace("_", " ")

        text = " ".join(text.split())

        return text
    @staticmethod
    async def match_product(product_name, item):

        text = await HSCodeService.normalize_text(
            json.dumps(item)
        )

        product_words = (
            await HSCodeService.normalize_text(
                product_name
            )
        ).split()

        matched_words = 0

        for word in product_words:

            if word in text:
                matched_words += 1

        score = matched_words / len(product_words)

        return score >= 0.7

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
    async def find_by_hs_code(self, hs_code):
        try:

            stmt = (
                select(
                    HSMaster,
                    Product,
                    Technical_regulation,
                    Standard
                )
                .outerjoin(Product, HSMaster.product_id == Product.id)
                .outerjoin(
                    Technical_regulation,
                    HSMaster.tr_id == Technical_regulation.id
                )
                .outerjoin(Standard, HSMaster.std_id == Standard.id)
                .where(
                    HSMaster.full_hs_code == hs_code,
                    HSMaster.is_deleted == False
                )
            )

            result = await self.db.execute(stmt)

            row = result.first()

            if not row:
                return None

            hs_master, product, tr, std = row

            response = jsonable_encoder(hs_master)

            response["product_data"] = (
            jsonable_encoder(product)
            if product else None
            )

            response["tr_data"] = (
                jsonable_encoder(tr)
                if tr else None
            )

            response["std_data"] = (
                jsonable_encoder(std)
                if std else None
            )

            return response

        except Exception as e:
            print(str(e))
            return None
   
def get_hs_code_service(
    db: AsyncSession = Depends(get_db)
):

    return HSCodeService(db)