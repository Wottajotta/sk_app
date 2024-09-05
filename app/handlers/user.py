from aiogram import Bot, Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaDocument

from app.db.requests import create_ticket, get_additionally_by_category, get_last_ticket, get_products, get_series, get_ticket, get_tickets_by_id, update_ticket
from app.handlers.user_group import get_tickets_media
from app.keyboards import inline, reply
from common.texts import admin_contact
from common.texts.group import group_id

user = Router()

list_images = []
list_documents = []


############################################### /start #####################################################################################
@user.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(f"Привет!👋\n\nЭтот бот создан для подачи и обработки региональных заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - Выбери пункт меню ниже👇", reply_markup= await inline.user_menu())
    
@user.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет!👋\n\nЭтот бот создан для подачи и обработки региональных заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - Выбери пункт меню ниже👇", reply_markup= await inline.user_menu())
    
    
@user.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(f"🤖 Бот-обработчик заявок создан и внедрен техническим отделом компании «СК УРАЛ»\n\n\
👨🏻‍💻 Разработчик/ТП: {admin_contact.text}", reply_markup= await inline.back_to_menu_from_help())
    
@user.callback_query(F.data==("support"))
async def help_cmd(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(f"🤖 Бот-обработчик заявок создан и внедрен техническим отделом компании «СК УРАЛ»\n\n\
👨🏻‍💻 Разработчик/ТП: {admin_contact.text}", reply_markup= await inline.back_to_menu_from_help())

############################################################################################################################################   
   
    
########## FSM-добавление новой заявки #####################################################################################################

class AddTicket(StatesGroup):
    user_id = State()
    region = State()
    category = State()
    series = State()
    product = State()
    additionally = State()
    additionally_value = State()
    images = State()
    documents = State()

    ticket_for_change = None
 
@user.callback_query(StateFilter(None), F.data.startswith("t-change_"))
async def change_ticket_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    ticket_id = callback.data.split("_")[-1]

    ticket_for_change = await get_ticket(int(ticket_id))

    AddTicket.ticket_for_change = ticket_for_change

    await callback.answer()
    await state.update_data(status="Отредактировано")
    await callback.message.answer("Выберите регион", 
                                  reply_markup=await reply.region())
    await state.set_state(AddTicket.region)  
   
    
@user.callback_query(F.data == "new_ticket")
async def new_ticket(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Меню заявок")
    await callback.message.answer("Добро пожаловать в меню заявок.", reply_markup=reply.new_ticket)
    await state.set_state(AddTicket.user_id)
    
    
# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@user.message(StateFilter("*"), Command("отмена"))
@user.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddTicket.ticket_for_change:
        AddTicket.ticket_for_change = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())
    
@user.message(AddTicket.user_id, F.text)
async def add_ticket_user_id(message: types.Message, state: FSMContext):
    await state.update_data(status="Новая")
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Выберите регион", reply_markup=await reply.region())
    await state.set_state(AddTicket.region)
    
@user.message(AddTicket.region, F.text)  
async def add_ticket_region(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(region=AddTicket.ticket_for_change.region)
    else:
        await state.update_data(region=message.text)
    await message.answer("Выберите категорию", reply_markup=await reply.categories())
    await state.set_state(AddTicket.category)
    
# Хендлер для отлова некорректных вводов для состояния region
@user.message(AddTicket.region)
async def add_ticket_region2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные, выберите регион!", 
                         reply_markup=await reply.region())
    
@user.message(AddTicket.category, F.text)
async def add_ticket_category(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(category=AddTicket.ticket_for_change.category)
    else:
        await state.update_data(category=message.text)
    await message.answer("Выберите серию", reply_markup=await reply.series(message.text))
    await state.set_state(AddTicket.series)
    
# Хендлер для отлова некорректных вводов для состояния category
@user.message(AddTicket.category)
async def add_ticket_category2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные, выберите категорию!", 
                         reply_markup=await reply.categories(message.text))
    
@user.message(AddTicket.series, F.text)
async def add_ticket_series(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(series=AddTicket.ticket_for_change.series)
    else:
        await state.update_data(series=message.text)
    await message.answer("Выберите продукт", reply_markup=await reply.product(message.text))
    await state.set_state(AddTicket.product)
    
# Хендлер для отлова некорректных вводов для состояния series
@user.message(AddTicket.series)
async def add_ticket_series2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные, выберите категорию!", 
                         reply_markup=await reply.series(message.text))
    
@user.message(AddTicket.product, F.text)
async def add_ticket_product(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(product=AddTicket.ticket_for_change.product)
    elif str(message.text) in [product.name for product in await get_products()]:
        await state.update_data(product=message.text)
        await message.answer("Выберите доп. опции", reply_markup=await reply.additionally_name())
        await state.set_state(AddTicket.additionally)
    else:
        await message.answer("Вы ввели недопустимые данные, выберите продукт используя кнопки ниже!")

#TODO Переделать выбор доп. опций    
@user.message(AddTicket.additionally, F.text)
async def add_ticket_additionally(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(additionally=AddTicket.ticket_for_change.additionally)
    additionallies = await get_additionally_by_category(state.get_data("category"))
    await state.update_data(additionally=message.text)
    btns = ["Без фото", "Закончить фотоотчет"]
    await message.answer("Приложите фото и нажмите на кнопку: Закончить фотоотчет", reply_markup=reply.get_callback_btns(btns=btns))
    await state.set_state(AddTicket.images)
    
    
@user.message(AddTicket.images)
async def add_ticket_images(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "Без фото":
        await state.update_data(images=None)
        btns = ["Без документов", "Закончить формирование заявки"]
        await message.answer("Приложите документ и нажмите на кнопку: Закончить формирование заявки", 
        reply_markup=reply.get_callback_btns(btns=btns))
        await state.set_state(AddTicket.documents)
    global list_images
    if message.photo:
        photo = message.photo[-1].file_id
        list_images.append(photo) 
    elif message.text == "Закончить фотоотчет":          
        await state.update_data(images=', '.join(list_images))
        btns = ["Без документов", "Закончить формирование заявки"]
        await message.answer("Приложите документ и нажмите на кнопку: Закончить формирование заявки", 
        reply_markup=reply.get_callback_btns(btns=btns))
        await state.set_state(AddTicket.documents)
 
async def send_ticket_to_group(bot, data, text):
    ticket = await get_last_ticket()
    region = ticket.region
    if region in group_id:
        value = group_id[region]
        await bot.send_message(chat_id=value, text=f"❗❗❗{text}❗❗❗\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: {ticket.series}\n\
Доп. информация: <strong>{ticket.additionally}</strong>",
    reply_markup=inline.get_callback_btns(btns={"Подробнее" : f"new-ticket_{ticket.id}"}))
        
@user.message(AddTicket.documents)
async def add_ticket_document(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    global list_documents
    if message.document:
        list_documents.append(message.document.file_id)
    elif message.text == "Закончить формирование заявки":
        await state.update_data(documents=', '.join(list_documents))
        data = await state.get_data()
        try:
            if AddTicket.ticket_for_change:
                
                await update_ticket(session, AddTicket.ticket_for_change.id, data)
                await send_ticket_to_group(bot, data, data["status"], "Заявка отредактирована")
            else:
                await create_ticket(session, data)
                await send_ticket_to_group(bot, data, data["status"], "Новая заявка")
            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Заявка успешно отправлена!\n\
Наши менеджеры уже приступили к обработке, ожидайте!", 
reply_markup=await inline.back_to_menu())
            await state.clear()
        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", 
                                 reply_markup=await inline.back_to_menu())
            await state.clear()

#############################################################################################################################


################################################### ТЕКУЩИЕ ЗАЯВКИ ##########################################################
@user.callback_query(F.data==("user_tickets"))
async def user_tickets(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    await callback.message.answer("Выберите статус заявки", reply_markup= reply.user_tickets)


@user.message(F.text=="Все заявки")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    
    all_tickets = await get_tickets_by_id(message.from_user.id)
    for ticket in all_tickets:
        await message.answer(f"ЗАЯВКА №{ticket.id}\n\n\
Статус: <strong>{ticket.status}</strong>\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: {ticket.series}\n\
Доп. информация: <strong>{ticket.additionally}</strong>", 
reply_markup=inline.get_callback_btns(
           btns={
               "Показать вложения": f"media-ticket_{ticket.id}",
               "Изменить": f"t-change_{ticket.id}",
           },
           sizes=(1,)
       ),)
    
    await message.answer("Вот все заявки от вашего имени ⏫", reply_markup=await inline.back_to_menu())

########
   
@user.message(F.text=="Новые заявки")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    
    all_tickets = await get_tickets_by_id(message.from_user.id)
    for ticket in all_tickets:
        if ticket.status == "Новая":
            await message.answer(f"ЗАЯВКА №{ticket.id}\n\n\
Статус: <strong>{ticket.status}</strong>\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: {ticket.series}\n\
Доп. информация: <strong>{ticket.additionally}</strong>", 
reply_markup=inline.get_callback_btns(
           btns={
               "Показать вложения": f"ticket-media_{ticket.id}",
               "Изменить": f"t-change_{ticket.id}",
           },
           sizes=(1,)
       ),)
    
    await message.answer("Вот все заявки от вашего имени ⏫", reply_markup=await inline.back_to_menu())
 
######## 
   
@user.message(F.text=="Заявки в работе")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    
    all_tickets = await get_tickets_by_id(message.from_user.id)
    for ticket in all_tickets:
        if ticket.status == "В работе":
            await message.answer(f"ЗАЯВКА №{ticket.id}\n\n\
Статус: <strong>{ticket.status}</strong>\n\
Регион: <strong>{ticket.region}</strong>\n\
Продукт: <strong>{ticket.product}</strong>\n\
Категория: <strong>{ticket.category}</strong>\n\
Серия: {ticket.series}\n\
Доп. информация: <strong>{ticket.additionally}</strong>", 
reply_markup=inline.get_callback_btns(
           btns={
               "Показать вложения": f"ticket-media_{ticket.id}",
               "Изменить": f"t-change_{ticket.id}",
           },
           sizes=(1,)
       ),)
    
    await message.answer("Вот все заявки от вашего имени ⏫", reply_markup=await inline.back_to_menu())
    
########
    
@user.callback_query(F.data.startswith("ticket-media_"))
async def get_ticket_media(callback: types.CallbackQuery, bot: Bot):

    await callback.answer()
    chat_id = callback.message.chat.id
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)

    photos = ticket.images
    documents = ticket.documents

    # Разделяем строки с ID на отдельные элементы, если строки не пустые
    photo_ids = photos.split(", ") if photos else []
    document_ids = documents.split(", ") if documents else []

    # Создаем список медиа объектов для отправки
    media_photos = []
    media_documents = []

    # Добавляем фото в медиа группу
    for photo_id in photo_ids:
        media_photos.append(InputMediaPhoto(media=photo_id))
    # Добавляем документы в медиа группу
    for doc_id in document_ids:
        media_documents.append(InputMediaDocument(media=doc_id))
    # Проверяем, есть ли медиа для отправки
    if media_photos or media_documents:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id=chat_id, media=media_photos + media_documents)
        await bot.send_message(chat_id, f"Медиа к заявке №{ticket.id}")
    if not media_photos and not media_documents:
        # Если нет медиа, отправляем уведомление
        await bot.send_message(chat_id, f"Нет медиа для отправки по заявке №{ticket.id}", reply_markup=await inline.back_to_menu())   
 
########
    
@user.callback_query(F.data.startswith("ticket-media_"))
async def get_finish_ticket_media(callback: types.CallbackQuery, bot: Bot):
    
    await callback.answer()
    
    chat_id = callback.message.chat.id
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)
    
    documents = ticket.finish_documents

    # Разделяем строки с ID на отдельные элементы, если строки не пустые
    document_ids = documents.split(", ") if documents else []

    # Создаем список медиа объектов для отправки
    media_documents = []
    # Добавляем документы в медиа группу
    for doc_id in document_ids:
        media_documents.append(InputMediaDocument(media=doc_id))
    # Проверяем, есть ли медиа для отправки
    if media_documents:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id=chat_id, media=media_documents)
        await bot.send_message(chat_id, f"Документы к заявке №{ticket.id}")
    if not media_documents:
        # Если нет документов, отправляем уведомление
        await bot.send_message(chat_id, f"Нет документов для отправки по заявке №{ticket.id}", reply_markup=await inline.back_to_menu())

#############################################################################################################################