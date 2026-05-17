from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
from urllib.parse import quote_plus

#  Async DB URL (IMPORTANT: asyncpg)

password = quote_plus(settings.DB_PASSWORD)
#  Async DB URL (IMPORTANT: asyncpg)
DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{password}@{settings.DB_HOST1}:{settings.DB_PORT}/{settings.DB_NAME}"

#  Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

#  Async Session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

#  Base
Base = declarative_base()


#  Dependency (ASYNC)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session