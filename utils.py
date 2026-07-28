import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

import database as db
from config import ADMIN_IDS, ALBUM_DEBOUNCE


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


_album_buffer: dict[str, list] = {}


async def collect_video_album(message):
    """Bitta yoki albom holida (bir vaqtda) yuborilgan videolarni yigʼadi.

    Hali yigʼish davom etayotgan boʼlsa None qaytaradi — chaqiruvchi hech narsa
    qilmasligi kerak (keyingi chaqiruv yakunlaydi). Yigʼish tugagach, shu albomdagi
    barcha video file_id larining roʼyxatini (yuborilgan tartibda) qaytaradi.
    """
    video = message.video
    if video is None:
        return None
    mgid = message.media_group_id
    if not mgid:
        return [video.file_id]

    key = f"{message.from_user.id}_{mgid}"
    _album_buffer.setdefault(key, []).append(video.file_id)
    before = len(_album_buffer[key])
    await asyncio.sleep(ALBUM_DEBOUNCE)
    after = len(_album_buffer[key])
    if before != after:
        return None
    return _album_buffer.pop(key)


async def get_not_subscribed_channels(bot: Bot, user_id: int):
    """Foydalanuvchi aʼzo boʼlmagan majburiy kanallar roʼyxatini qaytaradi."""
    channels = await db.get_channels()
    not_subscribed = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["channel_id"], user_id=user_id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(ch)
        except TelegramBadRequest:
            # Bot kanalda admin emas yoki kanal notoʼgʼri kiritilgan — oʼtkazib yuboramiz
            continue
    return not_subscribed
