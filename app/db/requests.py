from app.db.engine import async_session
from app.db.models import User, Region, Category, Series, Product, Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


########## Тут мы set и add ########## 
 
# Добавляем пользователя в БД
async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

# Добавляем регион в БД
async def add_region(session: AsyncSession, data: dict):
    obj = Region(
        name=data["name"],
    )
    session.add(obj)
    await session.commit()


########## Тут мы get, update и delete ########## 

# Достаем регионы
async def get_regions():
    async with async_session() as session:
        return await session.scalars(select(Region))

# Достаем категории
async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))