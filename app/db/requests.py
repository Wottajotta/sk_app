from app.db.engine import async_session
from app.db.models import User, Region, Category, Series, Product, Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete


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
    
# Добавляем категорию в БД
async def add_category(session: AsyncSession, data: dict):
    obj = Category(
        name=data["name"],
    )
    session.add(obj)
    await session.commit()
    
# Добавляем серию в БД
async def add_series(session: AsyncSession, data: dict):
    obj = Series(
        name=data["name"],
        category=data["category"]
    )
    session.add(obj)
    await session.commit()
    
# Добавляем продукт в БД
async def add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        category=data["category"],
        series=data["series"],
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
    
# Достаем категории
async def get_categories_name(id):
    async with async_session() as session:
        return await session.scalar(select(Category).where(Category.id==int(id)))
    
# Достаем категории
async def get_series():
    async with async_session() as session:
        return await session.scalars(select(Series))
    
# Достаем категории
async def get_products():
    async with async_session() as session:
        return await session.scalars(select(Product))
    
# Достаем категории
async def get_product(id):
    async with async_session() as session:
        return await session.scalars(select(Product).where(Product.id==int(id)))
    
# Достаем категории
async def get_products_сategory(text):
    async with async_session() as session:
        return await session.scalars(select(Product).where(Product.category==str(text)))
    
async def delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()
    
    
async def get_ticket(session: AsyncSession):
    return await session.scalars(select(Ticket))