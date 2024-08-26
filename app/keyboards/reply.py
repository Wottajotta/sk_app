from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from app.db.requests import (
    get_regions,
    get_categories,
    get_series,
    get_products,
)

# send_number = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Подтвердить номер", request_contact=True)
#         ]
#     ],
#     resize_keyboard=True,
#     input_field_placeholder="Отправьте телефон по кнопке ниже"
# )

new_ticket = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Новая заявка")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Начни заполнение по кнопки ниже"
)

async def region():
    all_regions = await get_regions()
    keyboard = ReplyKeyboardBuilder()
    
    for region in all_regions:
        keyboard.add(KeyboardButton(text=region.name))
        
    return keyboard.adjust(2).as_markup(resize_keyboard=True)

async def categories():
    all_categories = await get_categories()
    keyboard = ReplyKeyboardBuilder()
    
    for category in all_categories:
        keyboard.add(KeyboardButton(text=category.name))
        
    return keyboard.adjust(2).as_markup(resize_keyboard=True)

async def series():
    all_series = await get_series()
    keyboard = ReplyKeyboardBuilder()
    
    for series in all_series:
        keyboard.add(KeyboardButton(text=series.name))
        
    return keyboard.adjust(2).as_markup(resize_keyboard=True)

async def product():
    all_products = await get_products()
    keyboard = ReplyKeyboardBuilder()

    for product in all_products:
        keyboard.add(KeyboardButton(text=product.name))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


def get_callback_btns(*, btns):
    keyboard = ReplyKeyboardBuilder()

    for text in btns:
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)