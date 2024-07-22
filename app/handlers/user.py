from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.keyboards import reply

user = Router()


@user.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет!👋\n\nЭтот бот создан для обработок заявок в компании «СК УРАЛ»👨🏻‍💼\n\n\
Чтобы продолжить - подтверди свой номер телефона по кнопке ниже👇", reply_markup=reply.send_number)


