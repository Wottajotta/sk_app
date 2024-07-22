from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

from app.db.models import Base

engine = create_async_engine(os.getenv('DB_URL'), echo=True)
async_session = async_sessionmaker(engine)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)