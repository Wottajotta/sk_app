from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter, Filter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.keyboards import inline, reply
from common.texts import ticket_texts
from app.filters.chat_types import ChatTypeFilter, AdminProtect

from app.db.requests import (
    add_region,
    add_category,
    add_product,
    add_series,
    delete_product,
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
    
)


admin = Router()
admin.message.filter(ChatTypeFilter(["private"]), AdminProtect())

# Классы для FSM
class AddRegion(StatesGroup):
    name = State()

@admin.callback_query(F.data==("back_to_panel"))
async def back_to_panel(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(f"Привет!\n\n\
Это админ-панель, внизу ты найдешь все необходимое для настройки бота, удачи!", 
reply_markup=await inline.admin_menu())
    
@admin.message(Command("admin"))
async def admin_menu(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n\n\
Это админ-панель, внизу ты найдешь все необходимое для настройки бота, удачи!", 
reply_markup=await inline.admin_menu())
    
    

########## FSM-добавление регионов ##########
@admin.callback_query(F.data==("add_regions"))
async def add_regions(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.answer("Введите название региона:")
    await state.set_state(AddRegion.name)
    
# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin.message(StateFilter("*"), Command("отмена"))
@admin.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu_admin())
    
    
@admin.message(AddRegion.name, F.text)
async def add_region_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 120:
        await message.answer("Название региона не должно превышать 120 символов!")
        return
    
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await add_region(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Регион успешно добавлен!", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
        
###############################################################################################################################

################################################## FSM-добавление Категории ###################################################
class AddCategory(StatesGroup):
    name = State()
    
    
@admin.callback_query(F.data==("add_category"))
async def add_categories(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.answer("Введите название категории:")
    await state.set_state(AddCategory.name)
    
# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin.message(StateFilter("*"), Command("отмена"))
@admin.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu_admin())
    
    
@admin.message(AddCategory.name, F.text)
async def add_category_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 25:
        await message.answer("Название категории не должно превышать 25 символов!")
        return
    
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await add_category(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Категория успешно добавлена!", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
        
#############################################################################################################################

############################################## FSM-добавление Серии #########################################################
class AddSeries(StatesGroup):
    name = State()
    category = State()
    
    
@admin.callback_query(F.data==("add_series"))
async def add_series_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.answer("Введите название серии:")
    await state.set_state(AddSeries.name)
    
# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin.message(StateFilter("*"), Command("отмена"))
@admin.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu_admin())
    
    
@admin.message(AddSeries.name, F.text)
async def add_series_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 25:
        await message.answer("Название серии не должно превышать 25 символов!")
        return
    
    await state.update_data(name=message.text)
    await message.answer("Выберите категорию", reply_markup=await reply.categories())
    await state.set_state(AddSeries.category)
    
    
@admin.message(AddSeries.category, F.text)
async def add_series_category(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(category=message.text)
    data = await state.get_data()
    try:
        await add_series(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Серия успешно добавлена!", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
        
#############################################################################################################################

################################################### FSM-добавление Продукт ##################################################
class AddProduct(StatesGroup):
    name = State()
    category = State()
    series = State()
    
    product_for_change = None
    
    texts = {
        "AddProduct:category": "Выберите категорию заново ⬆️",
        "AddProduct:series": "Выберите серию заново ⬆️",
        "AddProduct:name": "Введите имя заново:",
    }
    
@admin.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]

    product_for_change = await get_product(int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)    

    
@admin.callback_query(F.data==("add_product"))
async def add_product_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.answer("Введите название Продукта:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)
    
# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin.message(StateFilter("*"), Command("отмена"))
@admin.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu_admin())

# Вернутся на шаг назад (на прошлое состояние)
@admin.message(StateFilter("*"), Command("назад"))
@admin.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer(
            'Предыдущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}"
            )
            return
        previous = step   
    
@admin.message(AddProduct.name, F.text)
async def add_product_category(message: types.Message, state: FSMContext, session: AsyncSession): 
    if len(message.text) > 120:
        await message.answer("Название продукта не должно превышать 120 символов!")
        return 
    await state.update_data(name=message.text)
    await message.answer("Выберите категорию", reply_markup=await reply.categories())
    await state.set_state(AddProduct.category)
    
    
@admin.message(AddProduct.category, F.text)
async def add_product_series(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(category=message.text)
    await message.answer("Выберите серию", reply_markup=await reply.series())
    await state.set_state(AddProduct.series)
    
@admin.message(AddProduct.series, F.text)
async def add_region_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(series=message.text)
    data = await state.get_data()
    try:
        await add_product(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Продукт успешно добавлен!", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
        
#############################################################################################################################


################################################### НОМЕНКЛАТУРА ############################################################
@admin.callback_query(F.data==("acitve_items"))
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
   
@admin.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await delete_product(session, int(product_id))

    await callback.answer("Товар удален")
    await callback.message.answer("Товар удален!")   


@admin.callback_query(F.data==("active_regions"))
async def active_regions(callback: types.CallbackQuery, session: AsyncSession):
   regions = await get_regions()
   await callback.answer()
   await iterating_items(callback, regions, "Вот список активных регионов ⏫", "delete-region")

@admin.callback_query(F.data==("active_category"))
async def active_regions(callback: types.CallbackQuery, session: AsyncSession):
   categories = await get_categories()
   await callback.answer()
   await iterating_items(callback, categories, "Вот список активных категорий товара ⏫", "delete-category")

@admin.callback_query(F.data==("active_series"))
async def active_regions(callback: types.CallbackQuery, session: AsyncSession):
   series = await get_series()
   await callback.answer()
   await iterating_items(callback, series, "Вот список активных серий товара ⏫", "delete-series")
   
   
@admin.callback_query(F.data==("active_product"))
async def active_product_category(callback: types.CallbackQuery, session: AsyncSession):
    categories = await get_categories()
    await callback.answer()
    btns = {category.name : f'p-category_{category.id}' for category in categories}
    await callback.message.answer("Выберите категорию", reply_markup=inline.get_callback_btns(btns=btns))

@admin.callback_query(F.data.startswith("p-category_"))
async def active_product(callback: types.CallbackQuery, session: AsyncSession):
   category_id = callback.data.split("_")[-1]
   categories = await get_categories_name(int(category_id))
   products = await get_products_сategory(categories.name)
   for product in products:
       await callback.message.answer(f"Наименование: <strong>{product.name}</strong>\n\
Категория: <strong>{product.category}</strong>\nСерия: {product.series}", 
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
   
@admin.callback_query(F.data==("active_additionally"))
async def active_additionally(callback: types.CallbackQuery, session: AsyncSession):
    categories = await get_categories()
    await callback.answer()
    btns = {category.name : f'a-category_{category.id}' for category in categories}
    await callback.answer()
    await callback.message.edit_text("Выберите категорию", reply_markup=inline.get_callback_btns(btns=btns))
 
@admin.callback_query(F.data.startswith("a-category_"))
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
    


   
#############################################################################################################################

###################################################### ТЕКУЩИЕ ЗАЯВКИ #######################################################

async def get_tickets(callback, status):
    
    t_region_id = callback.data.split("_")[-1]
    t_region = await get_regions_by_id(t_region_id)
    tickets = await get_tickets_by_region(t_region.name)
    
    for ticket in tickets:
        if status == "Новая" or status == "Отредактировано":
            btns={
            "Показать вложения" : f"ticket-media_{ticket.id}",
            "Принять в работу" : f"new-ticket-to-progress_{ticket.id}",
            "Удалить" : f"new-ticket-delete_{ticket.id}",
            }
        elif status == "В работе":
            btns={
            "Показать вложения" : f"ticket-media_{ticket.id}",
            "Завершить" : f"progress-ticket-to-finished_{ticket.id}",
            }
        
        elif status == "В работе":
            btns={
            "Показать вложения" : f"ticket-media_{ticket.id}",
            "Завершить" : f"progress-ticket-to-finished_{ticket.id}",
            }
        
        if ticket.status == status:
            await callback.answer()
            await callback.message.answer(f"Заявка <strong>№{ticket.id}</strong>\n\
Статус: <strong>{ticket.status}</strong>\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: <strong>{ticket.series}</strong>\n\
Доп. информация: <strong>{ticket.additionally}</strong>",
    reply_markup=inline.get_callback_btns(btns=btns,
    sizes=(1,)
    ),),
        elif ticket==None:
                await callback.message.answer("В данный момент нет новых заявок\n\n\
Выберите или введите команду /progress, для проосмотра заявок в работе", 
reply_markup=await inline.back_to_menu_admin())  
    
    await callback.answer()            
    await callback.message.answer("Вот список активных заявок ⏫", 
                                 reply_markup=await inline.back_to_menu_admin())


async def get_region_btns(callback, text):
    regions = await get_regions()
    await callback.answer()
    btns = {f"{region.name}": f"{text}region_{region.id}" for region in regions}
    await callback.message.answer("Выберите регион", reply_markup=inline.get_callback_btns(btns=btns))



@admin.callback_query(F.data.startswith("tickets_"))
async def current_ticket_region(callback: types.CallbackQuery, session: AsyncSession):
    region_id = callback.data.split("_")[-1]
    if region_id =="new":
       await get_region_btns(callback=callback, text="nt-")
    elif region_id =="progress":
        await get_region_btns(callback=callback, text="pt-")
    elif region_id =="finished":
        await get_region_btns(callback=callback, text="ft-")

@admin.callback_query(F.data.startswith("nt-region_"))
async def get_current_ticket(callback: types.CallbackQuery, session: AsyncSession):
    await get_tickets(callback=callback, status="Новая")
    
@admin.callback_query(F.data.startswith("pt-region_"))
async def get_current_ticket(callback: types.CallbackQuery, session: AsyncSession):
    await get_tickets(callback=callback, status="В работе")
    
@admin.callback_query(F.data.startswith("ft-region_"))
async def get_current_ticket(callback: types.CallbackQuery, session: AsyncSession):
    await get_tickets(callback=callback, status="Завершена")
    
@admin.callback_query(F.data.startswith("progress-ticket-to-finished_"))
async def finish_ticket(callback: types.CallbackQuery, session: AsyncSession):
    fticket_id = callback.data.split("_")[-1]
    ticket = await get_ticket(fticket_id)
    btns = ["Без закрывающих документов"]
    await callback.answer()
    await callback.message.answer(f"Приложите закрывающие документы по заявке №{ticket.id}\n\
На продукт {ticket.product}\n", reply_markup=reply.get_callback_btns(btns=btns))
    
    
######################################## Удаление #################################################
