from aiogram.filters import Filter
from aiogram import Bot, types

from config import ADMIN_LIST


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types
    

class AdminProtect(Filter):
    async def __call__(self, message: types.Message):
        return message.from_user.id in ADMIN_LIST