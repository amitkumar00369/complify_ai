from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from fastapi import Depends

from core.database import get_db
from app.utils.pagination import PaginationRsponse
from app.models.products import Product


# =========================
# PRODUCT SERVICE
# =========================
class ProductService:

    def __init__(self, db: AsyncSession):
        self.db = db

   
    async def get_all(self, find=None):
        try:
            

            stmt = (
                select(Product)
                .where(
                    Product.is_deleted == False
                )
                .order_by(
                    desc(Product.created_at)
                )
            )

            # dynamic filters
            if find:
                stmt = stmt.filter_by(**find)

            result = await self.db.execute(stmt)

            items = result.scalars().all()

            return jsonable_encoder(items)
        except Exception as e:
            print(str(e))
            return {}



# =========================
# DEPENDENCY INJECTION
# =========================
def get_product_service(
    db: AsyncSession = Depends(get_db)
):

    return ProductService(db)