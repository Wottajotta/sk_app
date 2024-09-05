from aiogram import Bot, Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter, Filter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.keyboards import inline, reply
from common.texts import ticket_texts
from app.filters.chat_types import ChatTypeFilter, AdminProtect

from app.db.requests import (
    get_additionally_by_category,
    get_categories_name,
    get_product,
    get_products_сategory,
    get_regions,
    get_categories,
    get_regions_by_id,
    get_series,
    get_products,
    get_ticket,
    get_tickets_by_region,
    update_product,
    
)


admin_nomenclature = Router()
admin_nomenclature.message.filter(ChatTypeFilter(["private"]), AdminProtect())

################################################### НОМЕНКЛАТУРА ############################################################
@admin_nomenclature.callback_query(F.data==("acitve_items"))
async def active_items(callback: types.CallbackQuery, session: AsyncSession):
   await callback.answer()
   await callback.message.answer("Какой именно раздел вас интересует?",
                                 reply_markup=await inline.active_items())
   
   
async def iterating_items(callback: types.CallbackQuery, iterating, text, callback_data):
    for item in iterating:
       await callback.message.answer(f"<strong>{item.name}</strong>", 
        reply_markup=inline.get_callback_btns(
           btns={
               "Удалить": f"{callback_data}_{item.id}",
           },
           sizes=(1,)
       ),
        )
    await callback.answer()
    await callback.message.answer(text, 
                                 reply_markup=await inline.back_to_menu_admin())
   
########

@admin_nomenclature.callback_query(F.data==("active_regions"))
async def active_regions(callback: types.CallbackQuery, session: AsyncSession):
   regions = await get_regions()
   await callback.answer()
   await iterating_items(callback, regions, "Вот список активных регионов ⏫", "delete-region")

########

@admin_nomenclature.callback_query(F.data==("active_category"))
async def active_regions(callback: types.CallbackQuery, session: AsyncSession):
   categories = await get_categories()
   await callback.answer()
   await iterating_items(callback, categories, "Вот список активных категорий товара ⏫", "delete-category")

########

@admin_nomenclature.callback_query(F.data==("active_series"))
async def active_regions(callback: types.CallbackQuery, session: AsyncSession):
   series = await get_series()
   await callback.answer()
   await iterating_items(callback, series, "Вот список активных серий товара ⏫", "delete-series")

######## 
   
@admin_nomenclature.callback_query(F.data==("active_product"))
async def active_product_category(callback: types.CallbackQuery, session: AsyncSession):
    categories = await get_categories()
    await callback.answer()
    btns = {category.name : f'p-category_{category.id}' for category in categories}
    await callback.message.answer("Выберите категорию", reply_markup=inline.get_callback_btns(btns=btns))

@admin_nomenclature.callback_query(F.data.startswith("p-category_"))
async def active_product(callback: types.CallbackQuery, session: AsyncSession):
   category_id = callback.data.split("_")[-1]
   categories = await get_categories_name(int(category_id))
   products = await get_products_сategory(categories.name)
   for product in products:
       await callback.message.answer(f"Наименование: <strong>{product.name}</strong>\n\
Категория: <strong>{product.category}</strong>\n\
Серия: {product.series}\n\
Комлпектация {product.equipment}", 
        reply_markup=inline.get_callback_btns(
           btns={
               "Изменить": f"change_{product.id}",
               "Удалить": f"delete-product_{product.id}",
           },
           sizes=(1,)
       ),
        )
   await callback.answer()
   await callback.message.answer("Вот список активной продукции ⏫", 
                                 reply_markup=await inline.back_to_menu_admin())

########
 
@admin_nomenclature.callback_query(F.data==("active_additionally"))
async def active_additionally(callback: types.CallbackQuery, session: AsyncSession):
    categories = await get_categories()
    await callback.answer()
    btns = {category.name : f'a-category_{category.id}' for category in categories}
    await callback.answer()
    await callback.message.edit_text("Выберите категорию", reply_markup=inline.get_callback_btns(btns=btns))
 
@admin_nomenclature.callback_query(F.data.startswith("a-category_"))
async def active_additionally2(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    category = await get_categories_name(int(category_id))
    additionallies = await get_additionally_by_category(category)
    for additionally in additionallies:
        await callback.message.answer(f"Наименование: <strong>{additionally.name}</strong>\n\
Категория: <strong>{additionally.category}</strong>\n\
Доступные значения:\n<strong>{additionally.value}</strong>",
        reply_markup=inline.get_callback_btns(
           btns={
               "Удалить": f"delete-additionally_{additionally.id}",
           },
           sizes=(1,)
       ),
        )
    await callback.answer()
    await callback.message.answer("Вот список активный доп. опций ⏫", 
                                 reply_markup=await inline.back_to_menu_admin())
#############################################################################################################################
