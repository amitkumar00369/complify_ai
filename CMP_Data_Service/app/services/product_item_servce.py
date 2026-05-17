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

    # =========================
    # CREATE
    # =========================
    async def create_product(self, data: dict):

        try:

            new_record = Product(**data)

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
    async def find_by_id(self, product_id: int):

        stmt = select(Product).where(
            Product.id == product_id,
            Product.is_deleted == False
        )

        result = await self.db.execute(stmt)

        product = result.scalar_one_or_none()

        return jsonable_encoder(product)

    # =========================
    # GET BY PRODUCT NAME
    # =========================
    async def get_by_product_name(
        self,
        product_name: str
    ):
        print("name",product_name)

        stmt = select(Product).where(
            Product.product_name == product_name,
            Product.is_deleted == False
        )

        result = await self.db.execute(stmt)

        product = result.scalar_one_or_none()

        return jsonable_encoder(product)

    # =========================
    # GET BY HS CODE
    # =========================
    async def get_by_hs_code(
        self,
        hs_code: str
    ):

        stmt = select(Product).where(
            Product.hs_code == hs_code,
            Product.is_deleted == False
        )

        result = await self.db.execute(stmt)

        products = result.scalars().all()

        return jsonable_encoder(products)

    # =========================
    # UPDATE
    # =========================
    async def find_by_id_update(
        self,
        product_id: int,
        payload: dict
    ):

        stmt = select(Product).where(
            Product.id == product_id,
            Product.is_deleted == False
        )

        result = await self.db.execute(stmt)

        product = result.scalar_one_or_none()

        if not product:
            return None

        for key, value in payload.items():

            setattr(product, key, value)

        await self.db.commit()

        await self.db.refresh(product)

        return jsonable_encoder(product)

    # =========================
    # DELETE (SOFT DELETE)
    # =========================
    async def delete_product(
        self,
        product_id: int
    ):

        stmt = select(Product).where(
            Product.id == product_id,
            Product.is_deleted == False
        )

        result = await self.db.execute(stmt)

        product = result.scalar_one_or_none()

        if not product:
            return None

        product.is_deleted = True

        await self.db.commit()

        return {
            "message": "Product deleted successfully"
        }

    # =========================
    # LIST PRODUCTS
    # =========================
    async def get_list(
        self,
        find=None,
        option={"page": 1, "limit": 10}
    ):

        stmt = (
            select(Product)
            .where(
                Product.is_deleted == False
            )
            .order_by(
                desc(Product.created_at)
            )
        )

        result = await self.db.execute(stmt)

        products = result.scalars().all()

        data = jsonable_encoder(products)

        return PaginationRsponse.returnData(
            data,
            option
        )


# =========================
# DEPENDENCY INJECTION
# =========================
def get_product_service(
    db: AsyncSession = Depends(get_db)
):

    return ProductService(db)