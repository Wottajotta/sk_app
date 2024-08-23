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
    get_regions,
    
)


admin = Router()
admin.message.filter(ChatTypeFilter(["private"]), AdminProtect())

# Классы для FSM
class AddRegion(StatesGroup):
    name = State()

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
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())
    
    
@admin.message(AddRegion.name, F.text)
async def add_region_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 120:
        await message.answer("Название региона не должно превышать 120 символов!")
        return
    
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await add_region(session, data)
        await message.answer("Регион успешно добавлен!", reply_markup=await inline.back_to_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu())
        await state.clear()
        
##################################################



########## FSM-добавление Категории ##########
class AddCategory(StatesGroup):
    ...