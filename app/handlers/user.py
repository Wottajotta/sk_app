from aiogram import Bot, Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaDocument

from app.db.requests import (
    create_ticket,
    get_additionally_by_category,
    get_additionally_by_name,
    get_categories,
    get_last_ticket,
    get_products_by_series,
    get_regions,
    get_series_by_categories,
    get_ticket,
    get_tickets_by_id,
    set_user,
    update_ticket,
)
from app.filters.chat_types import ChatTypeFilter
from app.keyboards import inline, reply
from common.texts import admin_contact
from common.texts.group import group_id

user = Router()

list_images = []
list_documents = []

# Массив для хранения названий и данных
name_list = []
data_list = []

user.message.filter(ChatTypeFilter(["private"]))


############################################### /start #####################################################################################
@user.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"Привет!👋\n\nЭтот бот создан для подачи и обработки региональных заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - Выбери пункт меню ниже👇",
        reply_markup=await inline.user_menu(),
    )


@user.message(CommandStart())
async def start_cmd(message: types.Message):
    await set_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет!👋\n\nЭтот бот создан для подачи и обработки региональных заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - Выбери пункт меню ниже👇",
        reply_markup=await inline.user_menu(),
    )


@user.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        f"🤖 Бот-обработчик заявок создан и внедрен техническим отделом компании «СК УРАЛ»\n\n\
👨🏻‍💻 Разработчик/ТП: {admin_contact.text}",
        reply_markup=await inline.back_to_menu_from_help(),
    )


@user.callback_query(F.data == ("support"))
async def help_cmd(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        f"🤖 Бот-обработчик заявок создан и внедрен техническим отделом компании «СК УРАЛ»\n\n\
👨🏻‍💻 Разработчик/ТП: {admin_contact.text}",
        reply_markup=await inline.back_to_menu_from_help(),
    )


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
    not_exist = State()
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
    await callback.message.answer("Выберите регион", reply_markup=await reply.region())
    await state.set_state(AddTicket.region)


@user.callback_query(F.data == "new_ticket")
async def new_ticket(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Меню заявок")
    await callback.message.answer(
        "Добро пожаловать в меню заявок.", reply_markup=reply.new_ticket
    )
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
    await message.answer("Отменяю...", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())


@user.message(AddTicket.user_id, F.text == "Новая заявка")
async def add_ticket_user_id(message: types.Message, state: FSMContext):
    await state.update_data(status="Новая")
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Выберите регион", reply_markup=await reply.region())
    await state.set_state(AddTicket.region)


@user.message(AddTicket.region, F.text)
async def add_ticket_region(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(region=AddTicket.ticket_for_change.region)
    elif str(message.text) in [region.name for region in await get_regions()]:
        await state.update_data(region=message.text)
        await message.answer(
            "Выберите категорию", reply_markup=await reply.categories()
        )
        await state.set_state(AddTicket.category)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите регион, используя кнопки ниже!"
        )


@user.message(AddTicket.category, F.text)
async def add_ticket_category(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(category=AddTicket.ticket_for_change.category)
    elif str(message.text) in [category.name for category in await get_categories()]:
        await state.update_data(category=message.text)
        await message.answer(
            "Выберите серию", reply_markup=await reply.series(message.text)
        )
        await state.set_state(AddTicket.series)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите категорию, используя кнопки ниже!"
        )


@user.message(AddTicket.series, F.text)
async def add_ticket_series(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(series=AddTicket.ticket_for_change.series)
    elif str(message.text) in [
        series.name for series in await get_series_by_categories(data.get("category"))
    ]:
        await state.update_data(series=message.text)
        await message.answer(
            "Выберите продукт", reply_markup=await reply.product(message.text)
        )
        await state.set_state(AddTicket.product)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите серию, используя кнопки ниже!"
        )


@user.message(AddTicket.product, F.text)
async def add_ticket_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(product=AddTicket.ticket_for_change.product)
    elif str(message.text) in [
        product.name for product in await get_products_by_series(data.get("series"))
    ]:
        await state.update_data(product=message.text)
        await message.answer(
            "Выберите доп. опции\nНажмите на кнопки с нужными названиями и нажмите «Далее»",
            reply_markup=await reply.additionally_name(data.get("category")),
        )
        await state.set_state(AddTicket.additionally)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите продукт, используя кнопки ниже!"
        )


# TODO Переделать выбор доп. опций
@user.message(AddTicket.additionally)
async def add_ticket_additionally(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    global name_list
    data = await state.get_data()

    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(product=AddTicket.ticket_for_change.additionally)
    # Проверка на "Далее"
    if message.text.strip() == "Далее":
        if not name_list:
            await message.reply("Вы не ввели ни одного названия.")
            return

        await state.set_state(AddTicket.additionally_value)
        await process_next_name(message, state)
        return  # Завершение функции после обработки "Далее"

    # Проверка на наличие текста в списке дополнительных опций
    additionally_options = [
        additionally.name
        for additionally in await get_additionally_by_category(data.get("category"))
    ]

    if message.text.strip() in additionally_options:
        name_list.append(message.text.strip())
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите доп. опции, используя кнопки ниже!"
        )


async def process_next_name(message: types.Message, state: FSMContext):
    if name_list:
        current_name = name_list.pop(0)
        await message.answer(
            f"Введите данные для '{current_name}':",
            reply_markup=await reply.additionally_value(current_name),
        )
        await state.update_data(current_name=current_name)
    else:
        all_data = ", ".join(data_list)
        await state.update_data(additionally_value=all_data)
        await message.answer(
            "Напишите комментарий к заявке или введите цифру 1 для пропуска",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.set_state(AddTicket.not_exist)


@user.message(AddTicket.additionally_value)
async def add_ticket_additionally_value(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    user_data = await state.get_data()
    current_name = user_data.get("current_name")
    all_additionally = await get_additionally_by_name(current_name)
    additionally_value_data = [add.strip() for add in all_additionally.split(", ")]

    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(
            additionally=AddTicket.ticket_for_change.additionally_value
        )
    elif str(message.text) in additionally_value_data:
        if current_name:
            data = message.text
            await message.answer(f"Вы ввели данные для '{current_name}': {data}")
            data_list.append(f"{current_name}: {data}")
            await process_next_name(message, state)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите значение доп. опции, используя кнопки ниже!"
        )


@user.message(AddTicket.not_exist)
async def add_ticket_not_exist(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text and message.text == "1":
        await state.update_data(not_exist="")
        btns = ["Без фото", "Закончить фотоотчет"]
        await message.answer(
            "Приложите фото и нажмите на кнопку: Закончить фотоотчет",
            reply_markup=reply.get_callback_btns(btns=btns),
        )
        await state.set_state(AddTicket.images)
    elif message.text and message.text != "1":
        await state.update_data(not_exist=message.text)
        btns = ["Без фото", "Закончить фотоотчет"]
        await message.answer(
            "Приложите фото и нажмите на кнопку: Закончить фотоотчет",
            reply_markup=reply.get_callback_btns(btns=btns),
        )
        await state.set_state(AddTicket.images)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, введите комментарий к заявке или введите цифру 1 для пропуска!"
        )


@user.message(AddTicket.images)
async def add_ticket_images(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "Без фото":
        await state.update_data(images="")
        btns = ["Закончить формирование заявки"]
        await message.answer(
            "Приложите документ и нажмите на кнопку: Закончить формирование заявки",
            reply_markup=reply.get_callback_btns(btns=btns),
        )
        await state.set_state(AddTicket.documents)
    global list_images
    if message.photo:
        photo = message.photo[-1].file_id
        list_images.append(photo)
    elif message.text == "Закончить фотоотчет":
        await state.update_data(images=", ".join(list_images))
        btns = ["Закончить формирование заявки"]
        await message.answer(
            "Приложите документ и нажмите на кнопку: Закончить формирование заявки",
            reply_markup=reply.get_callback_btns(btns=btns),
        )
        await state.set_state(AddTicket.documents)
    else:
        await message.answer("Вы ввели недопустимые данные, прикрепите фото!")


async def send_ticket_to_group(bot, text):
    # Получаем последнюю заявку
    ticket = await get_last_ticket()
    region = ticket.region

    # Проверяем, есть ли группа для данного региона
    if region in group_id:
        value = group_id[region]
        await bot.send_message(
            chat_id=value,
            text=(
                f"❗❗{text}❗❗\n"
                f"Регион: <strong>{ticket.region}</strong>\n"
                f"Продукт: <strong>{ticket.product}</strong>\n"
                f"Категория: <strong>{ticket.category}</strong>\n"
                f"Серия: {ticket.series}\n"
                f"Комплектация: {ticket.equipment}\n"
                f"Доп. информация: <strong>{ticket.additionally}</strong>\n"
                f"Комментарий: {ticket.not_exist}"
            ),
            reply_markup=inline.get_callback_btns(
                btns={"Подробнее": f"new-ticket_{ticket.id}"}
            ),
        )


@user.message(AddTicket.documents)
async def add_ticket_document(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    global list_documents, list_images, name_list, data_list

    # Проверяем, есть ли прикрепленный документ
    if message.document:
        list_documents.append(message.document.file_id)

    # Проверяем, завершил ли пользователь формирование заявки
    elif message.text == "Закончить формирование заявки":
        await state.update_data(documents=", ".join(list_documents))
        data = await state.get_data()

        try:
            # Если заявка редактируется, обновляем ее
            if AddTicket.ticket_for_change:
                await update_ticket(session, AddTicket.ticket_for_change.id, data)
                await send_ticket_to_group(bot, "Заявка отредактирована")
            else:
                # Иначе создаем новую заявку
                await create_ticket(session, data)
                await send_ticket_to_group(bot, "Новая заявка")

            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                "Заявка успешно отправлена!\nНаши менеджеры уже приступили к обработке, ожидайте!",
                reply_markup=await inline.back_to_menu(),
            )

            # Очищаем состояния и списки
            await state.clear()
            list_images.clear()
            list_documents.clear()
            name_list.clear()
            data_list.clear()

        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                f"Произошла ошибка: {e}, попробуйте ещё раз",
                reply_markup=await inline.back_to_menu(),
            )
            await state.clear()
            list_images.clear()
            list_documents.clear()
            name_list.clear()
            data_list.clear()

    else:
        await message.answer("Вы ввели недопустимые данные, прикрепите документы!")


#############################################################################################################################


################################################### ТЕКУЩИЕ ЗАЯВКИ ##########################################################
@user.callback_query(F.data == ("user_tickets"))
async def user_tickets(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    await callback.message.answer(
        "Выберите статус заявки", reply_markup=reply.user_tickets
    )


@user.message(F.text == "Все заявки")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    all_tickets = await get_tickets_by_id(message.from_user.id)

    if not all_tickets:
        await message.answer("У вас нет активных заявок.")
        return

    for ticket in all_tickets:
        if ticket.status == "Завершена":
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Показать завершающие документы": f"f-ticket-media_{ticket.id}",
            }
            status_emoji = "✅"
        else:
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Изменить": f"t-change_{ticket.id}",
            }
            status_emoji = (
                "❗"
                if ticket.status == "Новая"
                else "✏️" if ticket.status == "Отредактировано" else "🔧"
            )

        await message.answer(
            f"ЗАЯВКА №{ticket.id}\n\n"
            f"Статус: <strong>{ticket.status} {status_emoji}</strong>\n"
            f"Регион: <strong>{ticket.region}</strong>\n"
            f"Продукт: <strong>{ticket.product}</strong>\n"
            f"Категория: <strong>{ticket.category}</strong>\n"
            f"Серия: {ticket.series}\n"
            f"Комплектация: {ticket.equipment}\n"
            f"Доп. информация: <strong>{ticket.additionally}</strong>\n"
            f"Комментарий: {ticket.not_exist}",
            reply_markup=inline.get_callback_btns(btns=btns, sizes=(1,)),
        )

    await message.answer(
        "Вот все заявки от вашего имени ⏫", reply_markup=await inline.back_to_menu()
    )


########
async def get_user_tickets_by_status(message, status):
    all_tickets = await get_tickets_by_id(message.from_user.id)

    for ticket in all_tickets:
        btns = {}

        # Исправлено условие, чтобы проверять каждый статус отдельно
        if ticket.status in ["Новая", "Отредактировано", "В работе"]:
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Изменить": f"t-change_{ticket.id}",
            }
            status_emoji = (
                "❗"
                if ticket.status == "Новая"
                else "✏️" if ticket.status == "Отредактировано" else "🔧"
            )

        elif ticket.status == "Завершена":
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Показать завершающие документы": f"f-ticket-media_{ticket.id}",
            }
            status_emoji = "✅"

        # Проверяем, соответствует ли статус заявки искомому
        if ticket.status == status:
            await message.answer(
                f"ЗАЯВКА №{ticket.id}\n\n"
                f"Статус: <strong>{ticket.status} {status_emoji}</strong>\n"
                f"Регион: <strong>{ticket.region}</strong>\n"
                f"Продукт: <strong>{ticket.product}</strong>\n"
                f"Категория: <strong>{ticket.category}</strong>\n"
                f"Серия: {ticket.series}\n"
                f"Комплектация: {ticket.equipment}\n"
                f"Доп. информация: <strong>{ticket.additionally}</strong>\n"
                f"Комментарий: {ticket.not_exist}",
                reply_markup=inline.get_callback_btns(btns=btns, sizes=(1,)),
            )

    await message.answer(
        "Вот все заявки от вашего имени ⏫", reply_markup=await inline.back_to_menu()
    )


########


@user.message(F.text == "Новые заявки")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    await get_user_tickets_by_status(message, "Новая")


########


@user.message(F.text == "Отредактированные заявки")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    await get_user_tickets_by_status(message, "Отредактировано")


########


@user.message(F.text == "Заявки в работе")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    await get_user_tickets_by_status(message, "В работе")


########


@user.message(F.text == "Завершенные заявки")
async def all_user_tickets(message: types.Message, session: AsyncSession):
    await get_user_tickets_by_status(message, "Завершена")


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
    if media_photos:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id=chat_id, media=media_photos)
        await bot.send_message(chat_id, f"Фотографии к заявке №{ticket.id}")
    if media_documents:
        # Отправляем медиа группу
        await bot.send_media_group(chat_id=chat_id, media=media_documents)
        await bot.send_message(
            chat_id,
            f"Документы к заявке №{ticket.id}",
        )
    if not media_photos:
        # Если нет фото, отправляем уведомление
        await bot.send_message(chat_id, f"Нет фото для отправки по заявке №{ticket.id}")
    if not media_documents:
        # Если нет фото, отправляем уведомление
        await bot.send_message(
            chat_id,
            f"Нет документов для отправки по заявке №{ticket.id}",
        )
    if not media_documents and not media_photos:
        # Если нет медиа, отправляем уведомление
        await bot.send_message(
            chat_id, f"Нет медиа для отправки по заявке №{ticket.id}"
        )


########


@user.callback_query(F.data.startswith("f-ticket-media_"))
async def get_finish_ticket_media(callback: types.CallbackQuery, bot: Bot):

    await callback.answer()

    chat_id = callback.message.chat.id
    ticket_id = callback.data.split("_")[1]
    ticket = await get_ticket(ticket_id)

    documents = ticket.finish_documents
    document_ids = documents.split(", ") if documents else []

    media_documents = []
    for doc_id in document_ids:
        media_documents.append(InputMediaDocument(media=doc_id))
    if media_documents:
        await bot.send_media_group(chat_id=chat_id, media=media_documents)
        await bot.send_message(chat_id, f"Документы к заявке №{ticket.id}")
    if not media_documents:
        await bot.send_message(chat_id, f"Нет документов по заявке №{ticket.id}")


#############################################################################################################################
