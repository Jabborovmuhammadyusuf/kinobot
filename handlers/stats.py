from aiogram import Router, F
from aiogram.types import Message

import database as db
from utils import is_admin

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    total_users = await db.users_count()
    today_users = await db.users_count_today()
    movies_data = await db.movies_stats()
    total_views = await db.total_views()
    channels = await db.get_channels()
    top = await db.top_movies(5)

    text = (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🆕 Bugun qoʼshilgan: <b>{today_users}</b>\n\n"
        f"🎥 Kinolar soni: <b>{movies_data['movies']}</b>\n"
        f"📺 Seriallar soni: <b>{movies_data['series']}</b>\n"
        f"🎞 Serial qismlari jami: <b>{movies_data['series_parts']}</b>\n\n"
        f"👁 Jami koʼrishlar: <b>{total_views}</b>\n"
    )

    if top:
        text += "\n🏆 <b>Eng koʼp koʼrilgan kontent:</b>\n"
        for i, m in enumerate(top, 1):
            if m["views"] == 0:
                continue
            text += f"{i}. {m['title']} — {m['views']} koʼrish\n"

    if channels:
        text += "\n📢 <b>Kanallar statistikasi:</b>\n"
        for ch in channels:
            count = await db.channel_referral_count(ch["id"])
            text += f"• {ch['title']} — {count} ta obunachi\n"
    else:
        text += "\n📢 Hozircha majburiy kanallar qoʼshilmagan.\n"

    await message.answer(text)
