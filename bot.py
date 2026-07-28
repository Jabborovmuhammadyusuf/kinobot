import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db

from handlers import admin_menu, stats, channels, upload, add_episode, edit, broadcast, user


async def main():
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylida BOT_TOKEN ni kiriting.")

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Diqqat: tartib muhim! Admin-ga xos routerlar oldin, "user" routeri esa
    # oxirida ulanadi — chunki uning oxirgi handleri barcha matnlarni ushlab,
    # qidiruv sifatida qabul qiladi (fallback).
    dp.include_router(admin_menu.router)
    dp.include_router(stats.router)
    dp.include_router(channels.router)
    dp.include_router(upload.router)
    dp.include_router(add_episode.router)
    dp.include_router(edit.router)
    dp.include_router(broadcast.router)
    dp.include_router(user.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
