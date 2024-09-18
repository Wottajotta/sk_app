from aiogram import Bot, Router, types, F

from app.filters.chat_types import ChatTypeFilter
from config import ADMIN_LIST

fake = Router()

fake.message.filter(ChatTypeFilter(["private"]))


@fake.message(F.text)
async def fake_text(message: types.Message):
    if message.from_user.id in ADMIN_LIST:
        await message.answer("Вы отправили текст без назначения!\n\
Если хотите воспользоваться ботом, пожалуйста, используйте команды:\n<strong>/start - меню пользователя</strong>\n\
<strong>/admin - админ-панель</strong>")
    else:
        await message.answer("Вы отправили текст без назначения!\n\
Если хотите воспользоваться ботом, пожалуйста, используйте меню -> /start")
        
        
@fake.message(F.sticker)
async def fake_text(message: types.Message):
    sticker = message.sticker.file_id
    await message.answer_sticker(sticker)

async def fake_item(message,text):
    if message.from_user.id in ADMIN_LIST:
        await message.answer(f"Я очень рад, что вы делитесь со мной {text}, но я всего лишь бот!\n\
Если хотите воспользоваться ботом, пожалуйста, используйте команды:\n<strong>/start - меню пользователя</strong>\n\
<strong>/admin - админ-панель</strong>")
    else:
        await message.answer(f"Я очень рад, что вы делитесь со мной {text}, но я всего лишь бот!\n\
Если хотите воспользоваться ботом, пожалуйста, используйте меню -> /start")

@fake.message(F.photo)
async def fake_photo(message: types.Message):
   await fake_item(message, "фото")
        
@fake.message(F.document)
async def fake_document(message: types.Message):
    await fake_item(message, "документами")
        
@fake.message(F.video)
async def fake_video(message: types.Message):
    await fake_item(message, "видео")
        

@fake.message(F.audio)
async def fake_audio(message: types.Message):
    await fake_item(message, "музыкой")