from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from app.db.requests import get_regions


# send_number = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Подтвердить номер", request_contact=True)
#         ]
#     ],
#     resize_keyboard=True,
#     input_field_placeholder="Отправьте телефон по кнопке ниже"
# )


async def region():
    all_regions = await get_regions()
    keyboard = ReplyKeyboardBuilder()
    
    for region in all_regions:
        keyboard.add(KeyboardButton(text=region.name, callback_data=f'region_{region.id}'))
        
    return keyboard.adjust(2).as_markup()