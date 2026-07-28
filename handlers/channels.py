from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

import database as db
import keyboards as kb
from states import ChannelState
from utils import is_admin

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))


@router.message(F.text == "📢 Kanallar boshqaruvi")
async def channels_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📢 Kanallar boshqaruvi:", reply_markup=kb.channels_menu())


@router.message(F.text == "➕ Kanal qoʼshish")
async def ask_channel(message: Message, state: FSMContext):
    await state.set_state(ChannelState.waiting_channel)
    await message.answer(
        "📢 Kanal username'ini (@kanal) yoki ID raqamini yuboring.\n\n"
        "⚠️ Diqqat: bot shu kanalda admin boʼlishi shart!",
        reply_markup=kb.cancel_kb(),
    )


@router.message(ChannelState.waiting_channel)
async def save_channel(message: Message, state: FSMContext, bot: Bot):
    identifier = message.text.strip()
    try:
        chat = await bot.get_chat(identifier)
    except TelegramBadRequest:
        await message.answer(
            "❌ Kanal topilmadi. Bot kanalda admin ekanligiga va username toʼgʼri "
            "kiritilganiga ishonch hosil qiling."
        )
        return

    row_id = await db.add_channel(str(chat.id), chat.username or "", chat.title)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ch_{row_id}"

    await state.clear()
    await message.answer(
        f"✅ Kanal qoʼshildi: <b>{chat.title}</b>\n\n"
        f"Ushbu kanal orqali kelgan foydalanuvchilarni hisoblash uchun quyidagi "
        f"referal havoladan foydalaning (uni shu kanalda joylashtiring):\n\n"
        f"<code>{link}</code>",
        reply_markup=kb.channels_menu(),
    )


@router.message(F.text == "📋 Kanallar roʼyxati")
async def list_channels(message: Message):
    channels = await db.get_channels()
    if not channels:
        await message.answer("📋 Hozircha kanallar qoʼshilmagan.")
        return
    text = "📋 <b>Majburiy kanallar:</b>\n\n"
    for ch in channels:
        count = await db.channel_referral_count(ch["id"])
        username = f"@{ch['channel_username']}" if ch["channel_username"] else ch["channel_id"]
        text += f"• <b>{ch['title']}</b> ({username}) — {count} ta obunachi\n"
    await message.answer(text, reply_markup=kb.channel_remove_kb(channels))


@router.callback_query(F.data.startswith("remove_channel_"))
async def remove_channel(callback: CallbackQuery):
    row_id = int(callback.data.replace("remove_channel_", ""))
    await db.remove_channel(row_id)
    await callback.answer("🗑 Kanal oʼchirildi")
    await callback.message.delete()
