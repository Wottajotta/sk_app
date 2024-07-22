from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


send_number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Подтвердить номер", request_contact=True)
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Отправьте телефон по кнопке ниже"
)