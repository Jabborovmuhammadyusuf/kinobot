from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import SearchState
from utils import is_admin, get_not_subscribed_channels

router = Router()


async def send_subscription_prompt(message: Message, bot: Bot, channels):
    me = await bot.get_me()
    await message.answer(
        "📢 Botdan foydalanish uchun quyidagi kanallarga aʼzo boʼling, "
        "soʼng \"✅ Aʼzo boʼldim\" tugmasini bosing:",
        reply_markup=kb.subscribe_kb(channels, me.username),
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    args = message.text.split(maxsplit=1)
    source_channel = None
    if len(args) > 1 and args[1].startswith("ch_"):
        source_channel = args[1].replace("ch_", "", 1)

    await db.add_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
        source_channel,
    )

    not_subscribed = await get_not_subscribed_channels(bot, message.from_user.id)
    if not_subscribed:
        await send_subscription_prompt(message, bot, not_subscribed)
        return

    if is_admin(message.from_user.id):
        await message.answer(
            "🛠 Admin panelga xush kelibsiz!", reply_markup=kb.admin_main_menu()
        )
    else:
        await message.answer(
            "🎬 Kino botga xush kelibsiz!\n\n"
            "Kino yoki serial kodini yuboring, yoki nomi boʼyicha qidiring.",
            reply_markup=kb.user_menu(),
        )


@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    not_subscribed = await get_not_subscribed_channels(bot, callback.from_user.id)
    if not_subscribed:
        await callback.answer("❗️ Siz hali barcha kanallarga aʼzo boʼlmadingiz", show_alert=True)
        return
    await callback.message.delete()
    if is_admin(callback.from_user.id):
        await callback.message.answer("✅ Tasdiqlandi!", reply_markup=kb.admin_main_menu())
    else:
        await callback.message.answer(
            "✅ Tasdiqlandi! Endi kino kodini yuboring yoki nomi boʼyicha qidiring.",
            reply_markup=kb.user_menu(),
        )


async def deliver_movie_info(message: Message, movie):
    if movie["type"] == "movie":
        parts = await db.get_parts(movie["code"])
        if not parts:
            await message.answer("⚠️ Bu kino uchun video topilmadi.")
            return
        caption = f"🎬 <b>{movie['title']}</b>\n\n{movie['description']}"
        await message.answer_video(parts[0]["file_id"], caption=caption)
        await db.log_view(movie["code"], message.from_user.id)
    else:
        status = "♾ Davom etmoqda" if movie["is_ongoing"] else "✅ Yakunlangan"
        text = (
            f"📺 <b>{movie['title']}</b>\n\n"
            f"{movie['description']}\n\n"
            f"Holati: {status}\n"
            f"Mavjud qismlar: {movie['total_parts']} ta\n\n"
            f"Qismni tanlang 👇"
        )
        await message.answer(
            text, reply_markup=kb.parts_keyboard(movie["code"], movie["total_parts"])
        )


@router.callback_query(F.data.startswith("part_"))
async def send_part(callback: CallbackQuery):
    _, code, part_number = callback.data.split("_", 2)
    part = await db.get_part(code, int(part_number))
    if not part:
        await callback.answer("Qism topilmadi", show_alert=True)
        return
    movie = await db.get_movie(code)
    await callback.message.answer_video(
        part["file_id"],
        caption=f"📺 {movie['title']} — {part_number}-qism",
        reply_markup=kb.back_to_parts_kb(code),
    )
    await db.log_view(code, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("open_"))
async def open_movie(callback: CallbackQuery):
    code = callback.data.replace("open_", "", 1)
    movie = await db.get_movie(code)
    if not movie:
        await callback.answer("Topilmadi", show_alert=True)
        return
    await callback.message.delete()
    await deliver_movie_info(callback.message, movie)
    await callback.answer()


@router.message(F.text == "🔍 Kino qidirish")
async def ask_search_query(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await message.answer("🔎 Kino/serial nomini yoki kodini yuboring:")


@router.message(SearchState.waiting_query)
async def process_search(message: Message, state: FSMContext):
    await state.clear()
    await handle_search_text(message)


async def handle_search_text(message: Message):
    query = message.text.strip()
    movie = await db.get_movie(query)
    if movie:
        await deliver_movie_info(message, movie)
        return

    results = await db.search_movies_by_title(query)
    if not results:
        await message.answer("😔 Hech narsa topilmadi. Kodni yoki nomni tekshirib qayta yuboring.")
        return
    if len(results) == 1:
        await deliver_movie_info(message, results[0])
        return
    await message.answer(
        f"🔎 \"{query}\" boʼyicha {len(results)} ta natija topildi:",
        reply_markup=kb.search_results_kb(results),
    )


# Har qanday oddiy matn (admin menyu tugmalari va boshqa handlerlarga mos kelmasa)
# kino qidiruv sifatida qabul qilinadi. Bu handler routerlar zanjirining oxirida
# ulanadi (bot.py da), shu sababli admin buyruqlari ustuvor boʼladi.
@router.message(F.text & ~F.text.startswith("/"))
async def fallback_search(message: Message):
    await handle_search_text(message)
