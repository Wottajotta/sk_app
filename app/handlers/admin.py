from aiogram import Bot, Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter, Filter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.keyboards import inline, reply
from common.texts import ticket_texts
from app.filters.chat_types import ChatTypeFilter, AdminProtect

from app.db.requests import (
    add_additionally,
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
    update_product,
    
)


list_additionally = []
list_documents = []

admin = Router()
admin.message.filter(ChatTypeFilter(["private"]), AdminProtect())


############################################ Старт/back ########################################################################

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
   
################################################################################################################################    

############################################ FSM-добавление регионов ###########################################################
class AddRegion(StatesGroup):
    name = State()

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
    equipment = State()
    
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
    await message.answer("Выберите серию", reply_markup=await reply.series(message.text))
    await state.set_state(AddProduct.series)
    
@admin.message(AddProduct.series, F.text)
async def add_product_equipment(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(series=message.text)
    await message.answer("Укажите комплектацию", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.equipment)
    
@admin.message(AddProduct.equipment, F.text)
async def add_region_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(equipment=message.text)
    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await update_product(session, AddProduct.product_for_change.id, data)
        else:
            await add_product(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Продукт успешно добавлен/отредактирован!", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
        await state.clear()
        
#############################################################################################################################

############################################### FSM-добавление доп. опций ###################################################

class AddAdditionally(StatesGroup):
    category = State()
    name = State()
    value = State()


@admin.callback_query(F.data==("add_additionally"))
async def add_additionally_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.answer("Выберите категорию товара:", reply_markup=await reply.categories())
    await state.set_state(AddAdditionally.category)
    
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
    
@admin.message(AddAdditionally.category, F.text)
async def add_additionally_category(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(category=message.text)
    await message.answer("Введите название доп. опции:")
    await state.set_state(AddAdditionally.name)
    
@admin.message(AddAdditionally.name, F.text)
async def add_additionally_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(name=message.text)
    btns = ["Закончить заполнение опции"]
    await message.answer("Введите значения доп. опций и нажмите кнопку ниже:", 
                         reply_markup=reply.get_callback_btns(btns=btns))
    await state.set_state(AddAdditionally.value)
    
@admin.message(AddAdditionally.value)
async def add_aditionally_value(message: types.Message, state: FSMContext, session: AsyncSession):
    global list_additionally
    if message.text and message.text != "Закончить заполнение опции":
        list_additionally.append(message.text)
    elif message.text == "Закончить заполнение опции":
        await state.update_data(value=", ".join(list_additionally))
        data = await state.get_data()
        try:
            await add_additionally(session, data)
            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Доп. опция успешно добавлена!", reply_markup=await inline.back_to_menu_admin())
            await state.clear()
        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
            await state.clear()


#############################################################################################################################

###################################################### ТЕКУЩИЕ ЗАЯВКИ #######################################################

class FinishDoc(StatesGroup):
    ticket_id = State()
    status = State()
    doc_id = State()

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
async def finish_ticket(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    fticket_id = callback.data.split("_")[-1]
    ticket = await get_ticket(fticket_id)
    btns = ["Без закрывающих документов"]
    await callback.answer()
    await callback.message.answer(f"Приложите закрывающие документы по заявке №{ticket.id}\n\
На продукт {ticket.product}\n", reply_markup=reply.get_callback_btns(btns=btns))
    await state.update_data(ticket_id=fticket_id)
    await state.set_state(FinishDoc.doc_id)
    
@admin.message(FinishDoc.doc_id)
async def finish_ticket_doc(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    global list_documents
    ticket_id = data["ticket_id"]
    ticket = await get_ticket(ticket_id)
    if message.document:
        list_documents.append(message.document.file_id)
    elif message.text == "Закончить формирование заявки" or message.text == "Без закрывающих документов":
        if message.text == "Без закрывающих документов":
            await state.update_data(documents=None)
        elif message.text == "Закончить формирование заявки":
            await state.update_data(documents=', '.join(list_documents))
        state.update_data(status="Завершена")
        data = await state.get_data()
        try:
            await finish_ticket(session, ticket_id, data)
            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Заявка успешно завершена!", reply_markup=await inline.back_to_menu_admin())
            await bot.send_message(chat_id=ticket.tg_id, text=f"✅ Ваша заявка №{ticket.id} на продукт {ticket.product} успешно завершена!\n\
Чтобы посмотреть завершающие документы, нажми на кнопку ниже 👇🏻", reply_markup=inline.get_callback_btns(btns={"Показать закрывающие документы": f"ticket-media_{ticket.id}"}))
            await state.clear()
        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu_admin())
            await state.clear()

  
######################################## Удаление #################################################
