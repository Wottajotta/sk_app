import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from app.db.engine import async_main, async_session
from app.handlers.user_group import user_group
from app.handlers.user import user
from app.handlers.admin import admin
from app.handlers.nomenclature import admin_nomenclature
from app.middleware.db import DataBaseSession

load_dotenv()



async def main():
    await async_main()
    
    bot = Bot(os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    dp.include_routers(user, admin, user_group, admin_nomenclature)
    
    dp.update.middleware(DataBaseSession(session_pool=async_session))
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


  
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен!')
    