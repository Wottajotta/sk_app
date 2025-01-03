from app.db.engine import async_session
from app.db.models import Contractor, User, Region, Category, Series, Additionally, Product, Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


#################################### Тут мы set и add #############################################


# Добавляем пользователя в БД
async def set_user(tg_id, username=None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, username=username, is_admin="-"))
            await session.commit()


async def set_admin(tg_id):
    async with async_session() as session:
        query = update(User).where(User.tg_id == int(tg_id)).values(is_admin="+")
    await session.execute(query)
    await session.commit()


# Добавляем регион в БД
async def add_region(session: AsyncSession, data: dict):
    obj = Region(
        name=data["name"],
    )
    session.add(obj)
    await session.commit()

async def add_contractor(session: AsyncSession, data: dict):
    obj = Contractor(
        region=data["region"],
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
    obj = Series(name=data["name"], category=data["category"])
    session.add(obj)
    await session.commit()


# Добавляем продукт в БД
async def add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        category=data["category"],
        series=data["series"],
        equipment=data["equipment"],
    )

    session.add(obj)
    await session.commit()


async def update_product(session: AsyncSession, ticket_id: int, data):
    query = (
        update(Product)
        .where(Product.id == ticket_id)
        .values(
            name=data["name"],
            category=data["category"],
            series=data["series"],
            equipment=data["equipment"],
        )
    )
    await session.execute(query)
    await session.commit()


async def add_additionally(session: AsyncSession, data: dict):
    obj = Additionally(
        category=data["category"],
        name=data["name"],
        value=data["value"],
    )
    session.add(obj)
    await session.commit()


###################################################################################################

############################## Тут мы get, update и delete ########################################


async def get_users():
    async with async_session() as session:
        return await session.scalars(select(User))


async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == int(tg_id)))


async def get_admins(tg_id):
    async with async_session() as session:
        admin_users = await session.scalars(
            select(User.tg_id).where(User.tg_id == int(tg_id), User.is_admin == "+")
        )
        return admin_users.all()


# Достаем регионы
async def get_regions():
    async with async_session() as session:
        return await session.scalars(select(Region))


async def get_regions_by_id(id):
    async with async_session() as session:
        return await session.scalar(select(Region).where(Region.id == int(id)))

# Достаем контрагентов
async def get_contractors():
    async with async_session() as session:
        return await session.scalars(select(Contractor))
    
async def get_contractors_region():
    async with async_session() as session:
        return await session.scalars(select(Contractor.region))   
    
async def get_contractors_by_region(region):
    async with async_session() as session:
        return await session.scalars(select(Contractor).where(Contractor.region == region))

# Достаем категории
async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


# Достаем категории
async def get_categories_name(id):
    async with async_session() as session:
        return await session.scalar(select(Category.name).where(Category.id == int(id)))


# Достаем категории
async def get_series():
    async with async_session() as session:
        return await session.scalars(select(Series))


# Достаем категории
async def get_series_by_categories(category):
    async with async_session() as session:
        return await session.scalars(
            select(Series).where(Series.category == str(category))
        )


# Достаем категории
async def get_products():
    async with async_session() as session:
        return await session.scalars(select(Product))

async def get_product_equipment(name):
    async with async_session() as session:
        return await session.scalar(select(Product.equipment).where(Product.name==name))

# Достаем категории
async def get_product(session: AsyncSession, id):
    async with async_session() as session:
        return await session.scalar(select(Product).where(Product.id == int(id)))


# Достаем продукт
async def get_products_сategory(text):
    async with async_session() as session:
        return await session.scalars(
            select(Product).where(Product.category == str(text))
        )


async def get_products_by_series(text):
    async with async_session() as session:
        return await session.scalars(select(Product).where(Product.series == str(text)))


# Достаем доп. опции


async def get_additionally():
    async with async_session() as session:
        return await session.scalars(select(Additionally))


async def get_additionally_by_name(name):
    async with async_session() as session:
        return await session.scalar(
            select(Additionally.value).where(Additionally.name == str(name))
        )


async def get_additionally_by_category(category):
    async with async_session() as session:
        return await session.scalars(
            select(Additionally).where(Additionally.category == str(category))
        )


###################################################################################################


##################################### Работа с заявками ###########################################
async def create_ticket(session: AsyncSession, data: dict):
    obj = Ticket(
        status=data["status"],
        tg_id=data["user_id"],
        region=data["region"],
        contractor=data["contractor"],
        client=data["client"],
        number=data["number"],
        adress=data["adress"],
        date=data["date"],
        category=data["category"],
        series=data["series"],
        product=data["product"],
        equipment=data["equipment"],
        additionally=data["additionally_value"],
        comment=data["comment"],
        not_exist=data["not_exist"],
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
            additionally=data["additionally_value"],
            equipment=data["equipment"],
            not_exist=data["not_exist"],
            images=data["images"],
            documents=data["documents"],
        )
    )
    await session.execute(query)
    await session.commit()


async def finish_ticket(session: AsyncSession, ticket_id: int, data):
    query = (
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(
            status=data["status"],
            finish_documents=data["doc_id"],
        )
    )
    await session.execute(query)
    await session.commit()


async def get_tickets(session: AsyncSession):
    return await session.scalars(select(Ticket))


# Достаем последнюю запись в БД
async def get_last_ticket():
    async with async_session() as session:
        result = await session.execute(
            select(Ticket).order_by(Ticket.id.desc()).limit(1)
        )
        last_ticket = result.scalar_one_or_none()
        return last_ticket


# Достаем заявку
async def get_ticket(id):
    async with async_session() as session:
        return await session.scalar(select(Ticket).where(Ticket.id == int(id)))


# Достаем заявки по региону
async def get_tickets_by_region(region):
    async with async_session() as session:
        return await session.scalars(select(Ticket).where(Ticket.region == str(region)))


async def get_tickets_by_id(id):
    async with async_session() as session:
        return await session.scalars(select(Ticket).where(Ticket.tg_id == int(id)))


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
            finish_documents=doc_id,
        )
    )
    await session.execute(query)
    await session.commit()


###################################################################################################


##################################### Удаление позиций ############################################
async def del_admin(tg_id):
    async with async_session() as session:
        query = update(User).where(User.tg_id == int(tg_id)).values(is_admin="-")
    await session.execute(query)
    await session.commit()

async def del_contractor(id):
    async with async_session() as session:
        query = delete(Contractor).where(Contractor.id == int(id))
    await session.execute(query)
    await session.commit()

async def delete_region(session: AsyncSession, region_id):
    query = delete(Region).where(Region.id == int(region_id))
    await session.execute(query)
    await session.commit()


async def delete_category(session: AsyncSession, product_id):
    query = delete(Category).where(Category.id == int(product_id))
    await session.execute(query)
    await session.commit()


async def delete_series(session: AsyncSession, product_id):
    query = delete(Series).where(Series.id == int(product_id))
    await session.execute(query)
    await session.commit()


async def delete_product(session: AsyncSession, product_id):
    query = delete(Product).where(Product.id == int(product_id))
    await session.execute(query)
    await session.commit()


async def delete_additionally(session: AsyncSession, product_id):
    query = delete(Additionally).where(Additionally.id == int(product_id))
    await session.execute(query)
    await session.commit()


async def delete_ticket(session: AsyncSession, ticket_id):
    query = delete(Ticket).where(Ticket.id == int(ticket_id))
    await session.execute(query)
    await session.commit()
