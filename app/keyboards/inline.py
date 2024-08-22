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
        [InlineKeyboardButton(text='Добавить номенклатуру', callback_data='add_items')],
        [InlineKeyboardButton(text='Редактировать номенклатуру', callback_data='update_item')],
        [InlineKeyboardButton(text='Текущие заявки', callback_data='current_tickets')],
        [InlineKeyboardButton(text='Поддержка', callback_data="support")]
    ])

    return keyboard

async def back_to_menu():
    keyboard= InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_menu')]
    ])
    
    return keyboard