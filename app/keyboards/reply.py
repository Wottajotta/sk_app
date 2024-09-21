from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from app.db.requests import (
    get_additionally_by_category,
    get_additionally_by_name,
    get_products_by_series,
    get_regions,
    get_categories,
    get_series,
    get_products,
    get_series_by_categories,
)


new_ticket = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Новая заявка")]],
    resize_keyboard=True,
    input_field_placeholder="Начни заполнение по кнопки ниже",
)

user_tickets = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Все заявки"), KeyboardButton(text="Новые заявки")],
        [
            KeyboardButton(text="Отредактированные заявки"),
            KeyboardButton(text="Заявки в работе"),
        ],
        [KeyboardButton(text="Завершенные заявки")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите нужный тип заявок",
)


# Регионы
async def region():
    all_regions = await get_regions()
    keyboard = ReplyKeyboardBuilder()

    for region in all_regions:
        keyboard.add(KeyboardButton(text=region.name))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


# Категории
async def categories():
    all_categories = await get_categories()
    keyboard = ReplyKeyboardBuilder()

    for category in all_categories:
        keyboard.add(KeyboardButton(text=category.name))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


# Серия
async def series(category):
    all_series = await get_series_by_categories(category)
    keyboard = ReplyKeyboardBuilder()

    for series in all_series:
        keyboard.add(KeyboardButton(text=series.name))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


# Продукт
async def product(series):
    all_products = await get_products_by_series(series)
    keyboard = ReplyKeyboardBuilder()

    for product in all_products:
        keyboard.add(KeyboardButton(text=product.name))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


async def additionally_name(category):
    all_additionally = await get_additionally_by_category(category)
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(KeyboardButton(text="Далее"))
    for additionally in all_additionally:
        keyboard.add(KeyboardButton(text=additionally.name))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


async def additionally_value(name):
    all_additionally = await get_additionally_by_name(name)
    data = all_additionally.split(", ")

    keyboard = ReplyKeyboardBuilder()
    for additionally in data:
        keyboard.add(KeyboardButton(text=additionally))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


# Вспомогательные кнопки
def get_callback_btns(*, btns):
    keyboard = ReplyKeyboardBuilder()

    for text in btns:
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)
