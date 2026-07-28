from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import EditState
from utils import is_admin

router = Router()
router.message.filter(lambda message: is_admin(message.from_user.id))
router.callback_query.filter(lambda cq: is_admin(cq.from_user.id))


@router.message(F.text == "✏️ Kino tahrirlash")
async def ask_code_movie(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(target="movie")
    await state.set_state(EditState.waiting_code)
    await message.answer("🔑 Tahrirlamoqchi boʼlgan kino kodini kiriting:", reply_markup=kb.cancel_kb())


@router.message(F.text == "✏️ Serial tahrirlash")
async def ask_code_series(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(target="series")
    await state.set_state(EditState.waiting_code)
    await message.answer("🔑 Tahrirlamoqchi boʼlgan serial kodini kiriting:", reply_markup=kb.cancel_kb())


@router.message(EditState.waiting_code)
async def find_and_show_options(message: Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    target = data["target"]

    movie = await db.get_movie(code)
    if not movie:
        await message.answer("❌ Bunday kod topilmadi. Qayta kiriting:")
        return
    if movie["type"] != target:
        expected = "kino" if target == "movie" else "serial"
        await message.answer(f"❌ Bu kod {expected} emas. Toʼgʼri kodni kiriting:")
        return

    await state.update_data(code=code, title=movie["title"])
    label = "🎥" if target == "movie" else "📺"
    await message.answer(
        f"{label} <b>{movie['title']}</b>\n📝 {movie['description'] or '—'}\n\n"
        f"Nimani tahrirlaysiz?",
        reply_markup=kb.edit_fields_kb(target),
    )


@router.callback_query(F.data == "edit_title")
async def edit_title(callback: CallbackQuery, state: FSMContext):
    await state.update_data(field="title")
    await state.set_state(EditState.waiting_new_value)
    await callback.message.answer("📝 Yangi nomni kiriting:")
    await callback.answer()


@router.callback_query(F.data == "edit_description")
async def edit_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(field="description")
    await state.set_state(EditState.waiting_new_value)
    await callback.message.answer("📝 Yangi maʼlumot (tavsif) matnini kiriting:")
    await callback.answer()


@router.callback_query(F.data == "edit_status")
async def edit_status(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    movie = await db.get_movie(data["code"])
    new_status = not bool(movie["is_ongoing"])
    await db.update_movie_field(data["code"], "is_ongoing", int(new_status))
    text = "♾ Davom etmoqda" if new_status else "✅ Yakunlangan"
    await callback.message.answer(f"✅ Holat oʼzgartirildi: {text}", reply_markup=kb.content_menu())
    await state.clear()
    await callback.answer()


@router.message(EditState.waiting_new_value)
async def save_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["field"]
    code = data["code"]
    await db.update_movie_field(code, field, message.text.strip())
    await state.clear()
    label = "nomi" if field == "title" else "maʼlumoti"
    await message.answer(f"✅ Muvaffaqiyatli yangilandi ({label}).", reply_markup=kb.content_menu())


@router.callback_query(F.data == "edit_delete")
async def ask_delete_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer(
        f"⚠️ <b>{data['title']}</b> ({data['code']}) butunlay oʼchirilsinmi? "
        f"Bu amalni ortga qaytarib boʼlmaydi!",
        reply_markup=kb.confirm_delete_kb(data["code"]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def do_delete(callback: CallbackQuery, state: FSMContext):
    code = callback.data.replace("confirm_delete_", "", 1)
    await db.delete_movie(code)
    await state.clear()
    await callback.message.answer("🗑 Oʼchirildi.", reply_markup=kb.content_menu())
    await callback.answer()


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    await callback.message.answer("❌ Bekor qilindi.")
    await callback.answer()
