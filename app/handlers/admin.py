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
    get_regions,
    get_categories,
    get_series,
    get_products,
    
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
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())
    
    
@admin.message(AddCategory.name, F.text)
async def add_category_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) > 25:
        await message.answer("Название категории не должно превышать 25 символов!")
        return
    
    await state.update_data(name=message.text)
    data = await state.get_data()
    try:
        await add_category(session, data)
        await message.answer("Категория успешно добавлена!", reply_markup=await inline.back_to_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu())
        await state.clear()
        
#############################################################################################################################

########## FSM-добавление Серии ##########
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
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())
    
    
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
        await message.answer("Серия успешно добавлена!", reply_markup=await inline.back_to_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu())
        await state.clear()
        
#############################################################################################################################

########## FSM-добавление Продукт ##########################################################################################
class AddProduct(StatesGroup):
    name = State()
    category = State()
    series = State()
    
    texts = {
        "AddProduct:category": "Выберите категорию заново ⬆️",
        "AddProduct:series": "Выберите серию заново ⬆️",
        "AddProduct:name": "Введите имя заново:",
    }
    
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
    await message.answer("Действия отменены", reply_markup=await inline.back_to_menu())

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
    await message.answer("1/3", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Выберите категорию", reply_markup=await reply.categories())
    await state.set_state(AddProduct.category)
    
    
@admin.message(AddProduct.category, F.text)
async def add_product_series(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(category=message.text)
    await message.answer("2/3", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Выберите серию", reply_markup=await reply.series())
    await state.set_state(AddProduct.series)
    
@admin.message(AddProduct.series, F.text)
async def add_region_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(series=message.text)
    data = await state.get_data()
    try:
        await add_product(session, data)
        await message.answer("Продукт успешно добавлен!", reply_markup=await inline.back_to_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}, попробуйте ещё раз", reply_markup=await inline.back_to_menu())
        await state.clear()
        
#############################################################################################################################

