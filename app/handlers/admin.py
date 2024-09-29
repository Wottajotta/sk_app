from aiogram import Bot, Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.keyboards import inline, reply
from app.filters.chat_types import ChatTypeFilter, AdminProtect

from app.db.requests import (
    add_additionally,
    add_region,
    add_category,
    add_product,
    add_series,
    del_admin,
    finish_ticket,
    get_categories,
    get_product,
    get_regions,
    get_regions_by_id,
    get_series_by_categories,
    get_ticket,
    get_tickets_by_region,
    get_user,
    set_admin,
    update_product,
)


list_additionally = []
list_documents = []

admin = Router()
admin.message.filter(ChatTypeFilter(["private"]), AdminProtect())


############################################ Старт/back ########################################################################
@admin.message(Command("admin"))
async def admin_menu(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n\
Это админ-панель, внизу ты найдешь все необходимое для настройки бота, удачи!",
        reply_markup=await inline.admin_menu(),
    )


@admin.callback_query(F.data == ("back_to_panel"))
async def back_to_panel(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        f"Привет!\n\n\
Это админ-панель, внизу ты найдешь все необходимое для настройки бота, удачи!",
        reply_markup=await inline.admin_menu(),
    )


################################################################################################################################

############################################ Добавление Админа ###########################################################


@admin.callback_query(F.data == "add_admin")
async def show_user_list(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Выберите пользователя для назначения администратором:",
        reply_markup=await inline.get_users_inline(),
    )


@admin.callback_query(F.data.startswith("set-admin_"))
async def callback_set_admin(callback: types.CallbackQuery):
    tg_id = callback.data.split("_")[-1]
    user = await get_user(tg_id)
    await set_admin(int(tg_id))

    await callback.message.answer(
        f"Пользователь {user.username} ({tg_id}) назначен администратором.",
        reply_markup=await inline.back_to_menu_admin(),
    )
    await callback.answer()


@admin.callback_query(F.data == ("del_admin"))
async def del_admin_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Выберите пользователя для снятия администратора:",
        reply_markup=await inline.get_admins_inline(),
    )


@admin.callback_query(F.data.startswith("del-admin_"))
async def del2_admin_handler(callback: types.CallbackQuery):
    tg_id = callback.data.split("_")[-1]
    user = await get_user(tg_id)
    await del_admin(tg_id)

    await callback.message.answer(
        f"Пользователь {user.username} ({tg_id}) больше не администратор.",
        reply_markup=await inline.back_to_menu_admin(),
    )
    await callback.answer()


################################################################################################################################


############################################ FSM-добавление регионов ###########################################################
class AddRegion(StatesGroup):
    name = State()


@admin.callback_query(F.data == ("add_regions"))
async def add_regions(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
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
    await message.answer("Отменяю...", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(
        "Действия отменены", reply_markup=await inline.back_to_menu_admin()
    )


@admin.message(AddRegion.name, F.text)
async def add_region_name(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if len(message.text) > 120:
        await message.answer("Название региона не должно превышать 120 символов!")
        return

    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await add_region(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            "Регион успешно добавлен!", reply_markup=await inline.back_to_menu_admin()
        )
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            f"Произошла ошибка: {e}, попробуйте ещё раз",
            reply_markup=await inline.back_to_menu_admin(),
        )
        await state.clear()


###############################################################################################################################


################################################## FSM-добавление Категории ###################################################
class AddCategory(StatesGroup):
    name = State()


@admin.callback_query(F.data == ("add_category"))
async def add_categories(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
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
    await message.answer("Отменяю...", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(
        "Действия отменены", reply_markup=await inline.back_to_menu_admin()
    )


@admin.message(AddCategory.name, F.text)
async def add_category_name(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if len(message.text) > 25:
        await message.answer("Название категории не должно превышать 25 символов!")
        return

    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await add_category(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            "Категория успешно добавлена!",
            reply_markup=await inline.back_to_menu_admin(),
        )
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            f"Произошла ошибка: {e}, попробуйте ещё раз",
            reply_markup=await inline.back_to_menu_admin(),
        )
        await state.clear()


#############################################################################################################################


############################################## FSM-добавление Серии #########################################################
class AddSeries(StatesGroup):
    name = State()
    category = State()


@admin.callback_query(F.data == ("add_series"))
async def add_series_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
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
    await message.answer("Отменяю...", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(
        "Действия отменены", reply_markup=await inline.back_to_menu_admin()
    )


@admin.message(AddSeries.name, F.text)
async def add_series_name(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if len(message.text) > 25:
        await message.answer("Название серии не должно превышать 25 символов!")
        return

    await state.update_data(name=message.text)
    await message.answer("Выберите категорию", reply_markup=await reply.categories())
    await state.set_state(AddSeries.category)


@admin.message(AddSeries.category, F.text)
async def add_series_category(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if str(message.text) in [category.name for category in await get_categories()]:
        await state.update_data(category=message.text)
        data = await state.get_data()
        try:
            await add_series(session, data)
            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                "Серия успешно добавлена!",
                reply_markup=await inline.back_to_menu_admin(),
            )
            await state.clear()
        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                f"Произошла ошибка: {e}, попробуйте ещё раз",
                reply_markup=await inline.back_to_menu_admin(),
            )
            await state.clear()
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите серию, используя кнопки ниже!"
        )


#############################################################################################################################


################################################### FSM-добавление Продукт ##################################################
class AddProduct(StatesGroup):
    name = State()
    category = State()
    series = State()
    equipment = State()

    product_for_change = None


@admin.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]
    product_for_change = await get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change
    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin.callback_query(F.data == ("add_product"))
async def add_product_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.answer()
    await callback.message.answer(
        "Введите название Продукта:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin.message(StateFilter("*"), Command("отмена"))
@admin.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()
    await message.answer(
        "Действия отменены", reply_markup=await inline.back_to_menu_admin()
    )


@admin.message(AddProduct.name, F.text)
async def add_product_category(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if len(message.text) > 120:
            await message.answer("Название продукта не должно превышать 120 символов!")
            return
        await state.update_data(name=message.text)
    await message.answer("Выберите категорию", reply_markup=await reply.categories())
    await state.set_state(AddProduct.category)


# Хендлер для отлова некорректных вводов для состояния name
@admin.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст названия товара")


@admin.message(AddProduct.category, F.text)
async def add_product_series(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(category=AddProduct.product_for_change.category)
        await message.answer(
            "Выберите серию", reply_markup=await reply.series(message.text)
        )
        await state.set_state(AddProduct.series)
    elif str(message.text) in [category.name for category in await get_categories()]:
        await state.update_data(category=message.text)
        await message.answer(
            "Выберите серию", reply_markup=await reply.series(message.text)
        )
        await state.set_state(AddProduct.series)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите категорию, используя кнопки ниже!"
        )


@admin.message(AddProduct.series, F.text)
async def add_product_equipment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(series=AddProduct.product_for_change.series)
        await message.answer(
            "Укажите комплектацию или введите 1 для пропуска",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.set_state(AddProduct.equipment)
    elif str(message.text) in [
        series.name for series in await get_series_by_categories(data.get("category"))
    ]:
        await state.update_data(series=message.text)
        await message.answer(
            "Укажите комплектацию или введите 1 для пропуска",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.set_state(AddProduct.equipment)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите серию, используя кнопки ниже!"
        )


@admin.message(AddProduct.equipment, F.text)
async def add_product_equipment(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(equipment=AddProduct.product_for_change.equipment)
    if message.text == "1":
        await state.update_data(equipment="")
    else:
        await state.update_data(equipment=message.text)
    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await update_product(session, AddProduct.product_for_change.id, data)
        else:
            await add_product(session, data)
        await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            "Продукт успешно добавлен/отредактирован!",
            reply_markup=await inline.back_to_menu_admin(),
        )
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            f"Произошла ошибка: {e}, попробуйте ещё раз",
            reply_markup=await inline.back_to_menu_admin(),
        )
        await state.clear()
        AddProduct.product_for_change = None


#############################################################################################################################

############################################### FSM-добавление доп. опций ###################################################


class AddAdditionally(StatesGroup):
    category = State()
    name = State()
    value = State()


@admin.callback_query(F.data == ("add_additionally"))
async def add_additionally_handler(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.answer()
    await callback.message.answer(
        "Выберите категорию товара:", reply_markup=await reply.categories()
    )
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
    await message.answer(
        "Действия отменены", reply_markup=await inline.back_to_menu_admin()
    )


@admin.message(AddAdditionally.category, F.text)
async def add_additionally_category(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if str(message.text) in [category.name for category in await get_categories()]:
        await state.update_data(category=message.text)
        await message.answer(
            "Введите название доп. опции:", reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AddAdditionally.name)
    else:
        await message.answer(
            "Вы ввели недопустимые данные, выберите категорию, используя кнопки ниже!"
        )


@admin.message(AddAdditionally.name, F.text)
async def add_additionally_name(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(name=message.text)
    btns = ["Закончить заполнение опции"]
    await message.answer(
        "Введите значения доп. опций и нажмите кнопку ниже:",
        reply_markup=reply.get_callback_btns(btns=btns),
    )
    await state.set_state(AddAdditionally.value)


@admin.message(AddAdditionally.value)
async def add_aditionally_value(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    global list_additionally
    if message.text and message.text != "Закончить заполнение опции":
        list_additionally.append(message.text)
    elif message.text == "Закончить заполнение опции":
        await state.update_data(value=", ".join(list_additionally))
        data = await state.get_data()
        try:
            await add_additionally(session, data)
            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                "Доп. опция успешно добавлена!",
                reply_markup=await inline.back_to_menu_admin(),
            )
            list_additionally = []
            await state.clear()
        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                f"Произошла ошибка: {e}, попробуйте ещё раз",
                reply_markup=await inline.back_to_menu_admin(),
            )
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

    if not tickets:
        await callback.answer()
        await callback.message.answer(
            "В данный момент нет новых заявок\n\n"
            "Выберите или введите команду /progress, для просмотра заявок в работе",
            reply_markup=await inline.back_to_menu_admin(),
        )
        return

    for ticket in tickets:
        btns = {}
        if ticket.status in ["Новая", "Отредактировано"]:
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Принять в работу": f"new-ticket-to-progress_{ticket.id}",
                "Удалить": f"new-ticket-delete_{ticket.id}",
            }
        elif ticket.status == "В работе":
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Завершить": f"progress-ticket-to-finished_{ticket.id}",
            }
        elif ticket.status == "Завершена":
            btns = {
                "Показать вложения": f"ticket-media_{ticket.id}",
                "Завершающие документы": f"f-ticket-media_{ticket.id}",
            }

        if ticket.status == status:
            await callback.answer()
            await callback.message.answer(
                f"Заявка <strong>№{ticket.id}</strong>\n"
                f"Статус: <strong>{ticket.status}</strong>\n"
                f"Регион: <strong>{ticket.region}</strong>\n"
                f"Продукт: <strong>{ticket.product}</strong>\n"
                f"Категория: <strong>{ticket.category}</strong>\n"
                f"Серия: <strong>{ticket.series}</strong>\n"
                f"Комплектация: {ticket.equipment}\n"
                f"Доп. информация: <strong>{ticket.additionally}</strong>\n"
                f"Комментарий: {ticket.not_exist}",
                reply_markup=inline.get_callback_btns(btns=btns, sizes=(1,)),
            )

    await callback.answer()
    await callback.message.answer(
        "Вот список активных заявок ⏫", reply_markup=await inline.back_to_menu_admin()
    )


async def get_region_btns(callback, text):
    regions = await get_regions()
    await callback.answer()
    btns = {f"{region.name}": f"{text}region_{region.id}" for region in regions}
    await callback.message.answer(
        "Выберите регион", reply_markup=inline.get_callback_btns(btns=btns)
    )


@admin.callback_query(F.data.startswith("tickets_"))
async def current_ticket_region(callback: types.CallbackQuery, session: AsyncSession):
    region_id = callback.data.split("_")[-1]
    if region_id == "new":
        await get_region_btns(callback=callback, text="nt-")
    elif region_id == "progress":
        await get_region_btns(callback=callback, text="pt-")
    elif region_id == "finished":
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
async def finish_ticket_handler(
    callback: types.CallbackQuery, session: AsyncSession, state: FSMContext
):
    fticket_id = callback.data.split("_")[-1]
    ticket = await get_ticket(fticket_id)
    btns = ["Без закрывающих документов", "Закончить формирование заявки"]
    await callback.answer()
    await callback.message.answer(
        f"Приложите закрывающие документы по заявке №{ticket.id}\n\
На продукт {ticket.product}\n",
        reply_markup=reply.get_callback_btns(btns=btns),
    )
    await state.update_data(ticket_id=fticket_id)
    await state.set_state(FinishDoc.doc_id)


@admin.message(FinishDoc.doc_id)
async def finish_ticket_doc(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    global list_documents
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    ticket = await get_ticket(ticket_id)
    if message.document:
        list_documents.append(message.document.file_id)
    elif (
        message.text == "Закончить формирование заявки"
        or message.text == "Без закрывающих документов"
    ):
        if message.text == "Без закрывающих документов":
            await state.update_data(doc_id=None)
        elif message.text == "Закончить формирование заявки":
            await state.update_data(doc_id=", ".join(list_documents))
        await state.update_data(status="Завершена")
        data_f = await state.get_data()
        try:
            await finish_ticket(session, int(ticket_id), data_f)
            await message.answer("Успех ✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                "Заявка успешно завершена!",
                reply_markup=await inline.back_to_menu_admin(),
            )
            await bot.send_message(
                chat_id=int(ticket.tg_id),
                text=f"✅ Ваша заявка №{ticket.id} на продукт {ticket.product} успешно завершена!\n\
Чтобы посмотреть завершающие документы, нажми на кнопку ниже 👇🏻",
                reply_markup=inline.get_callback_btns(
                    btns={
                        "Показать закрывающие документы": f"f-ticket-media_{ticket.id}"
                    }
                ),
            )
            await state.clear()
        except Exception as e:
            await message.answer("Неудача ❌", reply_markup=types.ReplyKeyboardRemove())
            await message.answer(
                f"Произошла ошибка: {e}, попробуйте ещё раз",
                reply_markup=await inline.back_to_menu_admin(),
            )
            await state.clear()

