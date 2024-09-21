import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.db.models import Base

load_dotenv()
engine = create_async_engine(url=os.getenv("DB_URL"), echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
