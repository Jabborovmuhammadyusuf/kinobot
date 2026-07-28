import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# O'zingizda bor fayllardan import qilish:
from config import BOT_TOKEN  
from database import init_db

# Handler modullarini import qilish (agar ularni fayl sifatida alohida yozgan bo'lsangiz)
from handlers import admin_menu, stats, channels, upload, add_episode, edit, broadcast, user

import keyboards
import states
import utils

# Loggingni sozlash
logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi. .env yoki config.py faylida BOT_TOKEN ni kiriting.")

    await init_db()

    # Bot va Dispatcher yaratish (DefaultBotProperties yordamida HTML formatni yoqish)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash tartibi muhim
    dp.include_router(admin_menu.router)
    dp.include_router(stats.router)
    dp.include_router(channels.router)
    dp.include_router(upload.router)
    dp.include_router(add_episode.router)
    dp.include_router(edit.router)
    dp.include_router(broadcast.router)
    dp.include_router(user.router)

    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
