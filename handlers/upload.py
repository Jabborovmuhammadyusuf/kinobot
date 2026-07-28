from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import UploadState
from utils import is_admin, collect_video_album

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))
router.callback_query.filter(lambda cq: is_admin(cq.from_user.id))


@router.message(F.text == "🎥 Kino yuklash")
async def start_upload_movie(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(mode="movie")
    await state.set_state(UploadState.waiting_videos)
    await message.answer(
        "🎥 Kino videosini yuboring.\n\n"
        "ℹ️ Agar bir vaqtda bir nechta video yuborsangiz, bot buni avtomatik "
        "<b>serial</b> deb hisoblab, har birini alohida qism qilib saqlaydi.",
        reply_markup=kb.cancel_kb(),
    )


@router.message(F.text == "📺 Serial yuklash")
async def start_upload_series(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(mode="series")
    await state.set_state(UploadState.waiting_videos)
    await message.answer(
        "📺 Serial qismlarini yuboring (bittalab yoki bir nechtasini birga tanlab "
        "yuborishingiz mumkin).",
        reply_markup=kb.cancel_kb(),
    )


@router.message(UploadState.waiting_videos, F.video)
async def receive_videos(message: Message, state: FSMContext):
    videos = await collect_video_album(message)
    if videos is None:
        return  # albom hali yigʼilmoqda, keyingi chaqiruv yakunlaydi

    data = await state.get_data()
    mode = data.get("mode", "movie")
    actual_type = "series" if (mode == "series" or len(videos) > 1) else "movie"

    if actual_type == "series" and mode == "movie":
        await message.answer(
            f"ℹ️ {len(videos)} ta video aniqlandi — bu avtomatik <b>serial</b> "
            f"sifatida saqlanadi (har biri alohida qism)."
        )

    await state.update_data(videos=videos, actual_type=actual_type)
    await state.set_state(UploadState.waiting_code)
    await message.answer("🔑 Ushbu kontent uchun kod kiriting (masalan: 101):")


@router.message(UploadState.waiting_code)
async def receive_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if not code:
        await message.answer("❗️ Kod boʼsh boʼlishi mumkin emas. Qayta kiriting:")
        return
    if await db.movie_code_exists(code):
        await message.answer(
            "❌ Bu kod band (allaqachon mavjud). Boshqa, oʼzgacha kod kiriting:"
        )
        return
    await state.update_data(code=code)
    await state.set_state(UploadState.waiting_name)
    await message.answer("📝 Nomini kiriting:")


@router.message(UploadState.waiting_name)
async def receive_name(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    data = await state.get_data()

    if data["actual_type"] == "movie":
        await state.set_state(UploadState.waiting_description)
        await message.answer("ℹ️ Kino haqida maʼlumot (tavsif) kiriting:")
    else:
        await state.set_state(UploadState.waiting_status)
        await message.answer(
            "📌 Serial holatini tanlang:",
            reply_markup=kb.series_status_kb(),
        )


@router.callback_query(UploadState.waiting_status, F.data == "status_fixed")
async def status_fixed(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_ongoing=False)
    await state.set_state(UploadState.waiting_parts_count)
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "🔢 Jami nechta qism (yoki fasl) boʼlishini kiriting (masalan: 12):"
    )
    await callback.answer()


@router.callback_query(UploadState.waiting_status, F.data == "status_ongoing")
async def status_ongoing(callback: CallbackQuery, state: FSMContext):
    await state.update_data(is_ongoing=True, declared_parts=0)
    await state.set_state(UploadState.waiting_description)
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "ℹ️ Serial haqida maʼlumot (tavsif) kiriting:",
        reply_markup=kb.skip_description_kb(),
    )
    await callback.answer()


@router.message(UploadState.waiting_parts_count)
async def receive_parts_count(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗️ Iltimos, faqat son kiriting (masalan: 12):")
        return
    await state.update_data(declared_parts=int(message.text.strip()))
    await state.set_state(UploadState.waiting_description)
    await message.answer(
        "ℹ️ Serial haqida maʼlumot (tavsif) kiriting:",
        reply_markup=kb.skip_description_kb(),
    )


async def finalize_upload(message: Message, state: FSMContext, description: str):
    data = await state.get_data()
    code = data["code"]
    title = data["title"]
    actual_type = data["actual_type"]
    videos = data["videos"]

    await db.create_movie(
        code=code,
        type_=actual_type,
        title=title,
        description=description,
        is_ongoing=data.get("is_ongoing", False),
        declared_parts=data.get("declared_parts", 0),
    )
    for i, file_id in enumerate(videos, start=1):
        await db.add_part(code, i, file_id)

    await state.clear()

    if actual_type == "movie":
        summary = f"✅ Kino saqlandi!\n\n🔑 Kod: {code}\n📝 Nomi: {title}"
    else:
        status = "♾ Davom etmoqda" if data.get("is_ongoing") else "✅ Yakunlangan"
        summary = (
            f"✅ Serial saqlandi!\n\n🔑 Kod: {code}\n📝 Nomi: {title}\n"
            f"🎞 Yuklangan qismlar: 1-{len(videos)}\n📌 Holati: {status}"
        )
    await message.answer(summary, reply_markup=kb.content_menu())


@router.message(UploadState.waiting_description)
async def receive_description(message: Message, state: FSMContext):
    await finalize_upload(message, state, message.text.strip())


@router.callback_query(UploadState.waiting_description, F.data == "skip_description")
async def skip_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await finalize_upload(callback.message, state, "")
    await callback.answer()
