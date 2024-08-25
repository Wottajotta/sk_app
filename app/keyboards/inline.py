from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Стартовая клавиатура пользователя
async def user_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Оставить заявку', callback_data=f'new_ticket')],
        [InlineKeyboardButton(text='Мои заявки', callback_data='user_tickets')],
        [InlineKeyboardButton(text='Поддержка', callback_data="support")]
        
    ])
    
    return keyboard

#Админ-клавиатура
async def admin_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить регионы', callback_data='add_regions')],
        [InlineKeyboardButton(text='Добавить Категорию', callback_data='add_category')],
        [InlineKeyboardButton(text='Добавить Серию', callback_data='add_series')],
        [InlineKeyboardButton(text='Добавить Продукт', callback_data='add_product')],
        [InlineKeyboardButton(text='Номенклатура', callback_data='acitve_items')],
        [InlineKeyboardButton(text='Текущие заявки', callback_data='current_tickets')],
        [InlineKeyboardButton(text='Поддержка', callback_data="support")],
    ])

    return keyboard

async def active_items():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Регионы', callback_data='active_regions')],
        [InlineKeyboardButton(text='Категория', callback_data='active_category')],
        [InlineKeyboardButton(text='Серия', callback_data='active_series')],
        [InlineKeyboardButton(text='Продукция', callback_data='active_product')],
    ])

    return keyboard

async def back_to_menu():
    keyboard= InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')],
    ])
    
    return keyboard



async def back_to_menu_admin():
    keyboard= InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')],
        [InlineKeyboardButton(text='Вернуться в админ-панель', callback_data='back_to_panel')],
    ])
    
    return keyboard


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


