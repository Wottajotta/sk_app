from aiogram.filters import Filter
from aiogram import types

from app.db.requests import get_admins


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class AdminProtect(Filter):
    async def __call__(self, message: types.Message):
        admins = await get_admins(message.from_user.id)
        return message.from_user.id in admins
