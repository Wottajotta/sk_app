from aiogram import Bot, Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.db.requests import create_ticket, get_ticket
from app.keyboards import inline, reply
from common.texts import admin_contact

user = Router()

# /start
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
    
########## FSM-добавление новой заявки ##########

class AddTicket(StatesGroup):
    user_id = State()
    region = State()
    category = State()
    series = State()
    product = State()
    additionally = State()
    
    ticket_for_change = None
 
@user.callback_query(StateFilter(None), F.data.startswith("t-change_"))
async def change_ticket_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    ticket_id = callback.data.split("_")[-1]

    product_for_change = await get_ticket(int(ticket_id))

    AddTicket.ticket_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
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
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())
    
@user.message(AddTicket.user_id, F.text)
async def add_ticket_user_id(message: types.Message, state: FSMContext):
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
    
@user.message(AddTicket.category, F.text)
async def add_ticket_category(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(category=AddTicket.ticket_for_change.category)
    else:
        await state.update_data(category=message.text)
    await message.answer("Выберите серию", reply_markup=await reply.series())
    await state.set_state(AddTicket.series)
    
@user.message(AddTicket.series, F.text)
async def add_ticket_series(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(series=AddTicket.ticket_for_change.series)
    else:
        await state.update_data(series=message.text)
    await message.answer("Выберите продукт", reply_markup=await reply.product())
    await state.set_state(AddTicket.product)
    
@user.message(AddTicket.product, F.text)
async def add_ticket_product(message: types.Message, state: FSMContext):
    if message.text == "." and AddTicket.ticket_for_change:
        await state.update_data(product=AddTicket.ticket_for_change.product)
    else:
        await state.update_data(product=message.text)
    await message.answer("Введите дополнительную информацию", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTicket.additionally)
    
@user.message(AddTicket.additionally, F.text)
async def add_ticket_additionally(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(additionally=message.text)
    data = await state.get_data()
    try:
        await create_ticket(session, data)
        await message.answer("Успех ✅")
        await message.answer("Заявка успешно отправлена!\n\
Наши менеджеры уже приступили к обработке, ожидайте!", reply_markup=await inline.back_to_menu())
        await state.clear()
    except Exception as e:
        await message.answer("Неудача ❌")
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu())
        await state.clear()


