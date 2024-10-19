from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.requests import get_users

# Стартовая клавиатура пользователя
async def user_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Оставить заявку 💬', callback_data=f'new_ticket')],
        [InlineKeyboardButton(text='Мои заявки 📋', callback_data='user_tickets')],
        [InlineKeyboardButton(text='Поддержка 👨🏻‍💻', callback_data="support")]
        
    ])
    
    return keyboard


#Админ-клавиатура
async def admin_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Новые заявки ❗', callback_data='tickets_new')],
        [InlineKeyboardButton(text='Заявки в работе 🧾', callback_data='tickets_progress')],
        [InlineKeyboardButton(text='Завершенные заявки ✅', callback_data='tickets_finished')],
        [InlineKeyboardButton(text='Добавить Регионы ➕', callback_data='add_regions')],
        [InlineKeyboardButton(text='Добавить Категорию ➕', callback_data='add_category')],
        [InlineKeyboardButton(text='Добавить Серию ➕', callback_data='add_series')],
        [InlineKeyboardButton(text='Добавить Продукт ➕', callback_data='add_product')],
        [InlineKeyboardButton(text='Добавить Доп. Опции ➕', callback_data='add_additionally')],
        [InlineKeyboardButton(text='Номенклатура 📦', callback_data='acitve_items')],
        [InlineKeyboardButton(text='Добавить Администратора ➕', callback_data='add_admin')],
        [InlineKeyboardButton(text='Удалить Администратора ➖', callback_data='del_admin')],
        [InlineKeyboardButton(text='Добавить Контрагента ➕', callback_data='add_contractor')],
        [InlineKeyboardButton(text='Поддержка 👨🏻‍💻', callback_data="support")],
    ])

    return keyboard

async def active_items():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Регионы 🗺️', callback_data='active_regions')],
        [InlineKeyboardButton(text='Категория 🗂️', callback_data='active_category')],
        [InlineKeyboardButton(text='Серия 🗂️', callback_data='active_series')],
        [InlineKeyboardButton(text='Продукция 📦', callback_data='active_product')],
        [InlineKeyboardButton(text='Доп. опции 🧰', callback_data='active_additionally')],
        [InlineKeyboardButton(text='Контрагенты 🤵', callback_data='active_contractors')],
    ])

    return keyboard

async def back_to_menu():
    keyboard= InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в меню ☰', callback_data='back_to_menu')],
    ])
    
    return keyboard

async def back_to_menu_from_help():
    keyboard= InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Техническая поддержка 🤖', url="https://t.me/VA_b2b")],
        [InlineKeyboardButton(text='Вернуться в меню ☰', callback_data='back_to_menu')],
    ])
    
    return keyboard



async def back_to_menu_admin():
    keyboard= InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в меню ☰', callback_data='back_to_menu')],
        [InlineKeyboardButton(text='Вернуться в админ-панель 🛠️', callback_data='back_to_panel')],
    ])
    
    return keyboard

async def get_users_inline():
    users = await get_users()
        
    # Создаем инлайн-клавиатуру
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(
            InlineKeyboardButton(
            text=f"{user.username}",
            callback_data=f"set-admin_{user.tg_id}"
        ))
    return keyboard.adjust(2).as_markup()

async def get_admins_inline():
    users = await get_users()

    # Создаем инлайн-клавиатуру
    keyboard = InlineKeyboardBuilder()
    for user in users:
        if user.isAdmin == "+":
            keyboard.add(
                InlineKeyboardButton(
                text=f"{user.username}",
                callback_data=f"del-admin_{user.tg_id}"
            ))
    return keyboard.adjust(2).as_markup()

def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


