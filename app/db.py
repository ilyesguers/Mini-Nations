from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.async_database_url, pool_pre_ping=True, pool_recycle=300)
SessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def close_database() -> None:
    await engine.dispose()
