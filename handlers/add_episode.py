from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import AddEpisodeState
from utils import is_admin, collect_video_album

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))


@router.message(F.text == "➕ Yangi qism qoʼshish")
async def ask_series_code(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddEpisodeState.waiting_code)
    await message.answer(
        "🔑 Yangi qism qoʼshmoqchi boʼlgan serialning kodini kiriting:",
        reply_markup=kb.cancel_kb(),
    )


@router.message(AddEpisodeState.waiting_code)
async def find_series(message: Message, state: FSMContext):
    code = message.text.strip()
    movie = await db.get_movie(code)
    if not movie:
        await message.answer("❌ Bunday kod topilmadi. Qayta kiriting:")
        return
    if movie["type"] != "series":
        await message.answer(
            "❌ Bu kod kino (serial emas) uchun band. Yangi qism faqat serialga qoʼshiladi."
        )
        return

    last_part = await db.get_max_part_number(code)
    await state.update_data(code=code, last_part=last_part, title=movie["title"])
    await state.set_state(AddEpisodeState.waiting_videos)
    status = "♾ Davom etmoqda" if movie["is_ongoing"] else "✅ Yakunlangan"
    await message.answer(
        f"📺 <b>{movie['title']}</b> topildi.\n"
        f"Hozirgi qismlar: 1-{last_part}\n"
        f"Holati: {status}\n\n"
        f"➕ Yangi qism video(lar)ini yuboring (bittalab yoki bir nechtasini birga):"
    )


@router.message(AddEpisodeState.waiting_videos, F.video)
async def receive_new_episodes(message: Message, state: FSMContext):
    videos = await collect_video_album(message)
    if videos is None:
        return

    data = await state.get_data()
    code = data["code"]
    last_part = data["last_part"]
    title = data["title"]

    start = last_part + 1
    for i, file_id in enumerate(videos):
        await db.add_part(code, start + i, file_id)

    end = start + len(videos) - 1
    part_range = f"{start}" if start == end else f"{start}-{end}"

    await state.clear()
    await message.answer(
        f"✅ <b>{title}</b> serialiga yangi qism(lar) qoʼshildi: {part_range}-qism.",
        reply_markup=kb.content_menu(),
    )
