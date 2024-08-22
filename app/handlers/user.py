from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.keyboards import inline, reply
from common.texts import ticket_texts

user = Router()

class Ticket(StatesGroup):
    region = State()
    category = State()
    series = State()
    product = State()
    additionally = State()
    
    ticket_for_change = None




# /start
@user.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(f"Привет!👋\n\nЭтот бот создан для подачи и обработки региональных заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - Выбери пункт меню ниже👇", reply_markup= await inline.user_menu())
    
@user.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет!👋\n\nЭтот бот создан для подачи и обработки региональных заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - Выбери пункт меню ниже👇", reply_markup= await inline.user_menu())
    
    
    
@user.callback_query(F.data == "new_ticket")
async def new_ticket(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Выберите категорию из меню ниже")
    await callback.message.answer("Выберите регион", reply_markup= await reply.region())
    await state.set_state(Ticket.region)


