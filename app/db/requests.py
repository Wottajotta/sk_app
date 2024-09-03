from app.db.engine import async_session
from app.db.models import User, Region, Category, Series, Product, Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


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
    
async def get_regions_by_id(id):
    async with async_session() as session:
        return await session.scalar(select(Region).where(Region.id==int(id)))

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
    
async def get_products_by_series(text):
    async with async_session() as session:
        return await session.scalars(select(Product).where(Product.series==str(text)))
    
async def delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()
    
    


###################### Создание заявки #######################################
async def create_ticket(session: AsyncSession, data: dict):
    obj = Ticket(
        status=data["status"],
        tg_id=data["user_id"],
        region=data["region"],
        category=data["category"],
        series=data["series"],
        product=data["product"],
        additionally=data["additionally"],
        images=data["images"],
        documents=data["documents"],
    )
    session.add(obj)
    await session.commit()
       
async def update_ticket(session: AsyncSession, ticket_id: int, data):
    query = (
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(
            status=data["status"],
            region=data["region"],
            category=data["category"],
            series=data["series"],
            product=data["product"],
            additionally=data["additionally"],
            images=data["images"],
            documents=data["documents"],
        )
    )
    await session.execute(query)
    await session.commit()
    
async def get_tickets(session: AsyncSession):
    return await session.scalars(select(Ticket))

# Достаем последнюю запись в БД
async def get_last_ticket():
    async with async_session() as session:
        result = await session.execute(select(Ticket).order_by(Ticket.id.desc()).limit(1))
        last_ticket = result.scalar_one_or_none()
        return last_ticket
    
# Достаем заявку
async def get_ticket(id):
    async with async_session() as session:
        return await session.scalar(select(Ticket).where(Ticket.id==int(id)))
    
# Достаем заявки по региону
async def get_tickets_by_region(region):
    async with async_session() as session:
        return await session.scalars(select(Ticket).where(Ticket.region==str(region)))
    
    
async def get_tickets_by_id(id):
    async with async_session() as session:
        return await session.scalars(select(Ticket).where(Ticket.tg_id==int(id)))
    
async def update_ticket_status(session: AsyncSession, ticket_id, status: str):
    query = (
        update(Ticket)
        .where(Ticket.id == int(ticket_id))
        .values(
            status=status,
        )
    )
    await session.execute(query)
    await session.commit()
  
async def add_finished_documents(session: AsyncSession, ticket_id, doc_id: str):
    query = (
        update(Ticket)
        .where(Ticket.id == int(ticket_id))
        .values(
            finish_documents = doc_id,
        )
    )
    await session.execute(query)
    await session.commit()
  
async def delete_ticket(session: AsyncSession, ticket_id):
    query = delete(Ticket).where(Ticket.id == int(ticket_id))
    await session.execute(query)
    await session.commit()