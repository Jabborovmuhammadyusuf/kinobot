import asyncio

import aiosqlite
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import database as db
import keyboards as kb
from states import BroadcastState
from utils import is_admin

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))


@router.message(F.text == "📣 Xabar yuborish")
async def ask_broadcast(message: Message, state: FSMContext):
    await state.set_state(BroadcastState.waiting_message)
    await message.answer(
        "📣 Barcha foydalanuvchilarga yuboriladigan xabarni yuboring "
        "(matn, rasm, video — istalgan turdagi xabar boʼlishi mumkin):",
        reply_markup=kb.cancel_kb(),
    )


@router.message(BroadcastState.waiting_message)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    total = await db.users_count()
    await message.answer(f"⏳ Yuborilmoqda... ({total} ta foydalanuvchi)")

    async with aiosqlite.connect(db.DB_PATH) as conn:
        cur = await conn.execute("SELECT user_id FROM users")
        rows = await cur.fetchall()

    sent, failed = 0, 0
    for (user_id,) in rows:
        try:
            await message.copy_to(chat_id=user_id)
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(
        f"✅ Xabar yuborildi.\n📨 Muvaffaqiyatli: {sent}\n❌ Yuborilmadi: {failed}",
        reply_markup=kb.admin_main_menu(),
    )
